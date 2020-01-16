from flask import (Blueprint, request, current_app, jsonify)
from marshmallow import ValidationError
from jwt import (ExpiredSignatureError, PyJWTError)
from .serializers import ArtpieceSchema
from ..utilities import has_reached_monthly_submission_limit
from ..email import send_confirmation_email_async
from ..exceptions import (error_template, InvalidUsage, MONTLY_SUBMISSION_LIMIT_MESSAGE)
from ..user import User
from .artpiece import Artpiece
from web.extensions import db

artpiece_blueprint = Blueprint('artpiece', __name__)

@artpiece_blueprint.route('/artpiece', methods=('POST', ))
def receive_art():
    if has_reached_monthly_submission_limit(current_app.config['MONTLY_SUBMISSION_LIMIT']):
        raise InvalidUsage.reached_monthly_submission_limit()

    try:
        data = ArtpieceSchema().load(request.get_json())
    except ValidationError as err:
        raise InvalidUsage(**error_template(err.messages))

    user = User.get_by_email(data['email']) or User.from_email(data['email'])
    if user.has_active_submission():
        raise InvalidUsage.reached_user_limit()

    artpiece = user.create_artpiece(data['title'], data['art'])
    db.session.commit()

    send_confirmation_email_async(artpiece)

    success_msg = ('<b>One more step</b>: '
        'We\'re sending a confirmation email. Click the link there to confirm your art design')

    return jsonify({'success': success_msg}), 201
                

@artpiece_blueprint.route('/artpiece/confirm/<token>', methods=('PUT', ))
def confirm_artpiece(token):
    try:
        artpiece = Artpiece.verify_confirmation_token(token)
    except ExpiredSignatureError:
        raise InvalidUsage(**error_template('expired'))
    except PyJWTError:
        raise InvalidUsage(**error_template('invalid', 404))

    if artpiece.is_confirmed():
        success_type = 'already-confirmed'
    else:
        success_type = 'confirmed'
        artpiece.confirm()
        db.session.commit()

    return jsonify({'successType': success_type}), 200
