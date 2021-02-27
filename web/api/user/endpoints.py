from flask import (Blueprint, request, current_app, jsonify, send_file)
from flask_jwt_extended import jwt_required, create_access_token
from .exceptions import InvalidUsage
from .user import User
from web.extensions import db

import base64

from web.database.models import UserModel


user_blueprint = Blueprint('user', __name__, url_prefix='/user')

@user_blueprint.route('/login', methods=('POST', ))
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username != "test" or password != "test":
        return jsonify({"errors": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token.decode(), user=username)