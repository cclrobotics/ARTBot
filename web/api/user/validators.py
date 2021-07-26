from web.extensions import db
from .user import SuperUser
from .exceptions import InvalidUsage

def validate_user_existance(email, create_new_user):
    def user_exists(email):
        return SuperUser.get_by_email(email)

    if user_exists(email) and create_new_user:
        raise InvalidUsage.user_exists()
    if not user_exists(email) and not create_new_user:
        raise InvalidUsage.user_not_found()

def validate_user_token(user,created_at_timestamp):
    if not user.created_at.timestamp() == float(created_at_timestamp):
        raise InvalidUsage.bad_token()