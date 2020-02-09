import pytest
import json
from flask import current_app
from web.api.user.user import User
from web.database.models import ArtpieceModel

@pytest.fixture(scope="function")
def setup_app(test_app, test_database, clear_database):
    yield

def post_artpiece(email, title, art):
    return current_app.test_client().post(
            '/artpieces'
            , data=json.dumps({
                'email': email
                , 'title': title
                , 'art': art
            })
            , content_type='application/json'
        )

def update_monthly_limit(limit):
    monthly_limit = current_app.config['MONTLY_SUBMISSION_LIMIT']
    current_app.config['MONTLY_SUBMISSION_LIMIT'] = limit
    def revert():
        current_app.config['MONTLY_SUBMISSION_LIMIT'] = monthly_limit
    return revert

def create_artpiece_data(email, title, art):
    return {'email': email, 'title': title, 'art': art}

def get_artpiece_by_title(title):
    return ArtpieceModel.query.filter(ArtpieceModel.title == title).one_or_none()

@pytest.mark.usefixtures("setup_app")
def test_create_valid_artpiece():
    in_data = create_artpiece_data('randomtest@mail.com', 'random title', {'blue': [[0,0]]})
    rsp = post_artpiece(**in_data)
    assert rsp.status_code == 201
    artpiece = get_artpiece_by_title(in_data['title'])
    assert artpiece is not None
    user = User.get_by_id(artpiece.user_id)
    assert user is not None and user.email == in_data['email']

@pytest.mark.usefixtures("setup_app")
def test_create_artpiece_when_monthly_limit_exceeded():
    revert_monthly_limit = update_monthly_limit(0)
    rsp = post_artpiece('randomtest@mail.com', 'random title', {'blue': [[0, 0]]})
    revert_monthly_limit()
    assert rsp.status_code == 429
    data = json.loads(rsp.data.decode())
    assert data['errors'][0]['code'] == 'monthly_limit'

def create_artpiece(email, title, art):
    user = User.from_email(email)
    return user.create_artpiece(title, art)

@pytest.mark.usefixtures("setup_app")
def test_create_artpieces_with_same_email():
    in_data = create_artpiece_data('doubleofnothing@mail.com', 'is nothing', {'blue': [[0, 0]]})
    create_artpiece(**in_data)
    rsp = post_artpiece(**in_data)
    assert rsp.status_code == 429
    data = json.loads(rsp.data.decode())
    assert data['errors'][0]['code'] == 'user_limit'

@pytest.mark.usefixtures("setup_app")
@pytest.mark.parametrize("email", ['malformed@malformation', '@deadbeef', 'evil.universe'])
def test_create_artpiece_malformed_email(email):
    in_data = create_artpiece_data(email, 'malformed', {'blue': [[0, 0]]})
    rsp = post_artpiece(**in_data)
    assert rsp.status_code == 400
    data = json.loads(rsp.data.decode())
    assert data['errors'][0]['code'] == 'email'

@pytest.mark.usefixtures("setup_app")
@pytest.mark.parametrize("title", [None]+'`,~,!,@,#,$,%,^,&,*,/,\\,, ,  '.split(','))
def test_create_artpiece_non_alphanumeric_title(title):
    rsp = post_artpiece('valid@mail.com', title, {'blue': [[0, 0]]})
    assert rsp.status_code == 400
    data = json.loads(rsp.data.decode())
    assert data['errors'][0]['code'] == 'title'

@pytest.mark.usefixtures("setup_app")
@pytest.mark.parametrize("art", [{'blue': [[100, 0]]}, {'teal': [[5, 101]]}])
def test_create_artpiece_pixel_outofbounds(art):
    rsp = post_artpiece('valid@mail.com', 'valid title', art)
    assert rsp.status_code == 400
    data = json.loads(rsp.data.decode())
    assert data['errors'][0]['code'] == 'art'

@pytest.mark.usefixtures("setup_app")
def test_create_artpiece_unavailable_color():
    art_with_invalid_color = {'purplish': [[5, 5]]}
    rsp = post_artpiece('valid@mail.com', 'valid title', art_with_invalid_color)
    assert rsp.status_code == 400
    data = json.loads(rsp.data.decode())
    assert data['errors'][0]['code'] == 'art'

def post_artpiece_confirmation(id, token):
    return current_app.test_client().put(
            f'/artpieces/{id}/confirmation/{token}'
            , content_type='application/json'
        )

@pytest.mark.usefixtures("setup_app")
def test_confirm_artpiece():
    in_data = create_artpiece_data('regular@joe.com', 'artistic joe', {'pink': [[3,3], [5,5]]})
    artpiece = create_artpiece(**in_data)
    token = artpiece.get_confirmation_token()
    rsp = post_artpiece_confirmation(artpiece.id, token)
    assert rsp.status_code == 200
    data = json.loads(rsp.data.decode())
    assert data['data']['confirmation']['status'] == 'confirmed'

@pytest.mark.usefixtures("setup_app")
def test_confirmed_artpiece():
    in_data = create_artpiece_data('regular@joe.com', 'artistic joe', {'pink': [[3,3], [5,5]]})
    artpiece = create_artpiece(**in_data)
    artpiece.confirm()
    token = artpiece.get_confirmation_token()
    rsp = post_artpiece_confirmation(artpiece.id, token)
    assert rsp.status_code == 200
    data = json.loads(rsp.data.decode())
    assert data['data']['confirmation']['status'] == 'already_confirmed'

@pytest.mark.usefixtures("setup_app")
def test_expired_token_confirm_artpiece():
    in_data = create_artpiece_data('regular@joe.com', 'artistic joe', {'pink': [[3,3], [5,5]]})
    artpiece = create_artpiece(**in_data)
    token = artpiece.get_confirmation_token(expires_in=-1)
    rsp = post_artpiece_confirmation(artpiece.id, token)
    assert rsp.status_code == 400
    data = json.loads(rsp.data.decode())
    assert data['errors'][0]['code'] == 'token_expired'

@pytest.mark.usefixtures("setup_app")
def test_token_id_mismatch_confirm_artpiece():
    in_data = create_artpiece_data('regular@joe.com', 'artistic joe', {'pink': [[3,3], [5,5]]})
    artpiece = create_artpiece(**in_data)
    in_data['email'] = 'irregular@joe.com'
    mismatched_id = create_artpiece(**in_data).id

    token = artpiece.get_confirmation_token()
    rsp = post_artpiece_confirmation(mismatched_id, token)

    assert rsp.status_code == 404
    data = json.loads(rsp.data.decode())
    assert data['errors'][0]['code'] == 'token_invalid'

@pytest.mark.usefixtures("setup_app")
def test_invalid_token_confirm_artpiece():
    in_data = create_artpiece_data('invalid@token.com', 'invalid token', {'blue': [[1,1]]})
    artpiece = create_artpiece(**in_data)

    rsp = post_artpiece_confirmation(artpiece.id, 'oopsydaisy')

    assert rsp.status_code == 404
    data = json.loads(rsp.data.decode())
    assert data['errors'][0]['code'] == 'token_invalid'
