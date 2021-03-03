from flask import (Blueprint, request, current_app, jsonify, send_file)
from flask_jwt_extended import (
        create_access_token, create_refresh_token
        , set_access_cookies, set_refresh_cookies
    )
from .exceptions import InvalidUsage, error_template
from .user import User
from web.extensions import db

import base64

from web.database.models import UserModel


user_blueprint = Blueprint('user', __name__, url_prefix='/user')

@user_blueprint.route('/login', methods=('POST', ))
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.get_by_email(username)
    
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