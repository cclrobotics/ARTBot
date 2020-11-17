import pytest
import json
from flask import current_app
from web.api.user.user import User
from web.api.user.artpiece import (core, exceptions)
from web.api.user.exceptions import InvalidUsage
from web.database.models import ArtpieceModel

@pytest.fixture(scope="function")
def setup_app(test_app, test_database, clear_database):
    yield

VALID_EMAIL = 'valid@mail.com'
VALID_TITLE = 'valid title'
VALID_ART = {'1': [[0,0]], '2': [[1,1]], '3': [[2,2]]}
INITIAL_ROLE = 'Artist'


def create_artpiece_data(email=VALID_EMAIL, title=VALID_TITLE, art=VALID_ART):
    return {'email': email, 'title': title, 'art': art}

def create_artpiece(email=VALID_EMAIL, title=VALID_TITLE, art=VALID_ART):
    return User.from_email(email).create_artpiece(title, art)

@pytest.mark.usefixtures("setup_app")
def test_create_artpiece_by_new_user():
    artpiece = core.create_artpiece(VALID_EMAIL, VALID_TITLE, VALID_ART)
    assert artpiece.title == VALID_TITLE
    assert artpiece.creator.email == VALID_EMAIL
    assert artpiece.creator.role.value == INITIAL_ROLE

@pytest.mark.usefixtures("setup_app")
def test_monthly_submission_limit_exceeded():
    limit = 0
    with pytest.raises(exceptions.MonthlySubmissionLimitException):
        core.guarantee_monthly_submission_limit_not_reached(limit)
    create_artpiece()
    with pytest.raises(exceptions.MonthlySubmissionLimitException):
        core.guarantee_monthly_submission_limit_not_reached(limit)

@pytest.mark.usefixtures("setup_app")
def test_create_artpieces_with_same_email():
    with pytest.raises(exceptions.UserSubmissionLimitException):
        core.create_artpiece(VALID_EMAIL, VALID_TITLE, VALID_ART)
        core.create_artpiece(VALID_EMAIL, VALID_TITLE, VALID_ART)

@pytest.mark.usefixtures("setup_app")
@pytest.mark.parametrize('invalid_email', ['malformed@malformation', '@deadbeef', 'evil.universe'])
def test_create_artpiece_malformed_email(invalid_email):
    in_data = create_artpiece_data(email=invalid_email)
    with pytest.raises(InvalidUsage):
        core.validate_and_extract_artpiece_data(in_data, VALID_ART.keys())

@pytest.mark.usefixtures("setup_app")
@pytest.mark.parametrize('invalid_title', '`,~,!,@,#,$,%,^,&,*,/,\\,, ,  '.split(','))
def test_create_artpiece_non_alphanumeric_title(invalid_title):
    in_data = create_artpiece_data(title=invalid_title)
    with pytest.raises(exceptions.InvalidTitleException):
        core.validate_and_extract_artpiece_data(in_data, VALID_ART.keys())

@pytest.mark.usefixtures("setup_app")
@pytest.mark.parametrize('invalid_art', [{'1': [[100, 0]]}, {'2': [[5, 101]]}])
def test_create_artpiece_pixel_outofbounds(invalid_art):
    in_data = create_artpiece_data(art=invalid_art)
    with pytest.raises(exceptions.PixelOutOfBoundsException):
        core.validate_and_extract_artpiece_data(in_data, invalid_art.keys())

@pytest.mark.usefixtures("setup_app")
def test_create_artpiece_unavailable_color():
    art_with_invalid_color = {'10': [[5, 5]]}
    in_data = create_artpiece_data(art=art_with_invalid_color)
    with pytest.raises(exceptions.ColorSchemeException):
        core.validate_and_extract_artpiece_data(in_data, VALID_ART.keys())

@pytest.mark.usefixtures("setup_app")
@pytest.mark.parametrize('invalid_art', [{}, {'1': []}])
def test_create_artpiece_with_empty_canvas(invalid_art):
    in_data = create_artpiece_data(art=invalid_art)
    with pytest.raises(exceptions.BlankCanvasException):
        core.validate_and_extract_artpiece_data(in_data, VALID_ART.keys())

@pytest.mark.usefixtures("setup_app")
def test_confirm_artpiece():
    artpiece = create_artpiece()
    token = artpiece.get_confirmation_token()
    status = core.confirm_artpiece(artpiece, token)
    assert status == 'confirmed'

@pytest.mark.usefixtures("setup_app")
def test_confirmed_artpiece():
    artpiece = create_artpiece()
    artpiece.confirm()
    token = artpiece.get_confirmation_token()
    status = core.confirm_artpiece(artpiece, token)
    assert status == 'already_confirmed'

@pytest.mark.usefixtures("setup_app")
def test_expired_token_confirm_artpiece():
    artpiece = create_artpiece()
    token = artpiece.get_confirmation_token(expires_in=-1)

    with pytest.raises(exceptions.ExpiredConfirmationTokenException):
        core.confirm_artpiece(artpiece, token)

@pytest.mark.usefixtures("setup_app")
def test_token_id_mismatch_confirm_artpiece():
    artpiece_1 = create_artpiece()
    artpiece_2 = create_artpiece(email='other@mail.com')
    token_1 = artpiece_1.get_confirmation_token()

    with pytest.raises(exceptions.InvalidConfirmationTokenException):
        core.confirm_artpiece(artpiece_2, token_1)

@pytest.mark.usefixtures("setup_app")
def test_invalid_token_confirm_artpiece():
    artpiece = create_artpiece()
    with pytest.raises(exceptions.InvalidConfirmationTokenException):
        core.confirm_artpiece(artpiece, 'random_invalid_token')
