from functools import partial
from marshmallow import ValidationError
from web.extensions import db
from .validators import validate_user_token
from .serializers import SuperUserSchema
from .exceptions import InvalidUsage
from .user import SuperUser


def validate_and_extract_user_data(json_data, skipped_fields: tuple= (), new_user: bool=False):
    try:
        data = SuperUserSchema(new_user).load(json_data, partial=skipped_fields)
    except ValidationError as err:
        raise InvalidUsage.from_validation_error(err)
    return data


def create_superuser(email, password, role = SuperUser.default_role()):
    s_user = SuperUser.from_email(email, role=role)
    s_user.set_password(password)

    db.session.commit()
    return s_user.id, True

def update_superuser_role(email, new_role):
    s_user = SuperUser.get_by_email(email)
    old_role = s_user.role
    s_user.set_role(new_role)

    db.session.commit()
    return s_user.email, old_role.value, s_user.role.value

def update_superuser_password(email, new_password, created_at_timestamp):
    s_user = SuperUser.get_by_email(email)
    validate_user_token(s_user, created_at_timestamp)
    s_user.set_password(new_password)

    db.session.commit()
    return s_user.email, True

def delete_superuser(id, created_at_timestamp):
    """
    Delete a user record from the SuperUser table
    For added security, must provide exact creation datetime
    of the user, in timestamp format
    """
    s_user = SuperUser.get_by_id(id)
    validate_user_token(s_user, created_at_timestamp)
    s_user.delete()

    db.session.commit()
    return s_user.email, True