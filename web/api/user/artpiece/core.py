import datetime
import json
from marshmallow import ValidationError
from jwt import (ExpiredSignatureError, PyJWTError)
from .serializers import ArtpieceSchema
from .artpiece import (Artpiece, TokenIDMismatchError)
from .exceptions import (UserSubmissionLimitException, MonthlySubmissionLimitException,
        InvalidConfirmationTokenException, ExpiredConfirmationTokenException)
from ..user import User
from ..exceptions import InvalidUsage

def first_of_month():
    return datetime.date.today().replace(day=1)

def get_monthly_submission_count():
    return Artpiece.total_submission_count_since(first_of_month())

def has_reached_monthly_submission_limit(limit):
    return get_monthly_submission_count() >= limit

def guarantee_monthly_submission_limit_not_reached(limit):
    if has_reached_monthly_submission_limit(limit):
        raise MonthlySubmissionLimitException()

def validate_and_extract_artpiece_data(json_data, color_keys):
    try:
        data = ArtpieceSchema(color_keys).load(json_data)
    except ValidationError as err:
        raise InvalidUsage.from_validation_error(err)
    return data['email'], data['title'], data['art'], data['canvas_size']

def create_artpiece(email, title, art, canvas_size):
    user = User.get_by_email(email) or User.from_email(email)
    if user.has_active_submission():
        raise UserSubmissionLimitException()
    return user.create_artpiece(title, art, canvas_size)

def confirm_artpiece(artpiece, token):
    if artpiece is None:
        raise InvalidUsage.resource_not_found()

    try:
        artpiece.verify_confirmation_token(token)
    except ExpiredSignatureError:
        raise ExpiredConfirmationTokenException()
    except (PyJWTError, TokenIDMismatchError):
        raise InvalidConfirmationTokenException()

    if artpiece.is_confirmed():
        status = 'already_confirmed'
    else:
        status = 'confirmed'
        artpiece.confirm()

    return status
