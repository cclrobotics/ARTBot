from datetime import datetime
from flask_jwt_extended import jwt_required
from flask import (Blueprint, request, current_app, jsonify, send_file)
from flask_jwt_extended import (
        create_access_token, create_refresh_token
        , set_access_cookies, set_refresh_cookies
    )
from .core import (create_superuser, delete_superuser, validate_and_extract_user_data,
                   update_superuser_role, update_superuser_password
                  )
from .exceptions import InvalidUsage, error_template
from .user import SuperUser
from .utilities import access_level_required
from web.extensions.jwt_config import user_lookup_callback
from web.database.models import SuperUserRole

import base64


user_blueprint = Blueprint('user', __name__, url_prefix='/user')

@user_blueprint.route('/login', methods=('POST', ))
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = SuperUser.get_by_email(username)
    
    if user is None or user.password_hash is None or not user.is_password_valid(password):
        raise InvalidUsage.bad_login()

    if user.password_needs_rehash():
        user.set_password(password)

    # Create the tokens we will be sending back to the user
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    # Set the JWTs and the CSRF double submit protection cookies
    # in this response
    resp = jsonify({'login': True, 'user':user.email})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)

    return resp, 200


@user_blueprint.route('/remove/<id>/<created_at_timestamp>', methods=('PUT', ))
@jwt_required()
@access_level_required(SuperUserRole.admin)
def remove(id, created_at_timestamp):
    email, success = delete_superuser(id, created_at_timestamp)
    resp = jsonify({'user': email, 'deleted': success})
    return resp, 200


@user_blueprint.route('/create', methods=('POST', ))
@jwt_required()
@access_level_required(SuperUserRole.admin)
def create():
    data = validate_and_extract_user_data(request.json, new_user=True)
    email, password, role = data['email'], data['password'], data['role']

    id, success = create_superuser(email, password, role)

    resp = jsonify({'user_id': id, 'created': success})
    return resp, 200


@user_blueprint.route('/change_role', methods=('POST', ))
@jwt_required()
@access_level_required(SuperUserRole.admin)
def update_role():
    data = validate_and_extract_user_data(request.json, skipped_fields=('password',))
    email, requested_role = data['email'], data['role']

    email, old_role, new_role = update_superuser_role(email, requested_role)
    resp = jsonify({'user': email, 'old_role': old_role, 'new_role': new_role})
    return resp, 200


@user_blueprint.route('/reset_password/<created_at_timestamp>', methods=('POST', ))
@jwt_required()
@access_level_required(SuperUserRole.admin)
def reset_password(created_at_timestamp):
    data = validate_and_extract_user_data(request.json, skipped_fields=('role',))
    email, requested_password = data['email'], data['password']

    email, success = update_superuser_password(email, requested_password, created_at_timestamp)
    resp = jsonify({'user': email, 'success': success})
    return resp, 200