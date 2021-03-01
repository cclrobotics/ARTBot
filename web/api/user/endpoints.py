from flask import (Blueprint, request, current_app, jsonify, send_file)
from flask_jwt_extended import jwt_required, create_access_token
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
    if user is None or password == "" or not user.is_password_valid(password):
        raise InvalidUsage.bad_login()

    if user.password_needs_rehash():
        user.set_password(password)

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token.decode(), user=user.email)