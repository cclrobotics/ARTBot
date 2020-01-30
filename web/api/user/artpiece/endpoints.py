from flask import (Blueprint, request, current_app, jsonify)
from marshmallow import ValidationError
from jwt import (ExpiredSignatureError, PyJWTError)
from .serializers import ArtpieceSchema
from ..utilities import has_reached_monthly_submission_limit
from ..email import send_confirmation_email_async
from ..exceptions import InvalidUsage
from ..user import User
from .artpiece import (Artpiece, TokenIDMismatchError)
from web.extensions import db

artpiece_blueprint = Blueprint('artpiece', __name__)

@artpiece_blueprint.route('/artpieces', methods=('GET', ))
def get_artpieces_meta():
    monthly_limit = current_app.config['MONTLY_SUBMISSION_LIMIT']
    return jsonify(
            {
                'meta':
                {
                    'submission_limit_exceeded': has_reached_monthly_submission_limit(
                        monthly_limit)
                }
                , 'data': None
            }), 200

@artpiece_blueprint.route('/artpieces', methods=('POST', ))
def receive_art():
    if has_reached_monthly_submission_limit(current_app.config['MONTLY_SUBMISSION_LIMIT']):
        raise InvalidUsage.reached_monthly_submission_limit()

    try:
        data = ArtpieceSchema().load(request.get_json())
    except ValidationError as err:
        raise InvalidUsage.from_validation_error(err)

    user = User.get_by_email(data['email']) or User.from_email(data['email'])
    if user.has_active_submission():
        raise InvalidUsage.reached_user_limit()

    artpiece = user.create_artpiece(data['title'], data['art'])
    db.session.commit()

    send_confirmation_email_async(artpiece)

    return jsonify({'data': None}), 201


@artpiece_blueprint.route('/artpieces/<int:id>/confirmation/<token>', methods=('PUT', ))
def confirm_artpiece(id, token):
    artpiece = Artpiece.get_by_id(id)
    if artpiece is None:
        raise InvalidUsage.resource_not_found()

    try:
        artpiece.verify_confirmation_token(token)
    except ExpiredSignatureError:
        raise InvalidUsage.confirmation_token_expired()
    except (PyJWTError, TokenIDMismatchError):
        raise InvalidUsage.invalid_confirmation_token()

    if artpiece.is_confirmed():
        status = 'already_confirmed'
    else:
        status = 'confirmed'
        artpiece.confirm()
        db.session.commit()

    return jsonify({'data': {'confirmation': {'status': status}}}), 200
