#views.py - Maps URLs to backend functions, then returns the results to the appropriate view

from flask import (render_template, Blueprint, request, current_app, jsonify)
from marshmallow import ValidationError
from .serializers import ArtpieceSchema
from .utilities import has_reached_monthly_submission_limit
from .email import send_confirmation_email_async
from .exceptions import (error_template, InvalidUsage, MONTLY_SUBMISSION_LIMIT_MESSAGE)
from .user import User
from .extensions import db

main = Blueprint('main', __name__)

#Home page
@main.route('/', methods=('GET', ))
@main.route('/index', methods=('GET', ))
def index():
    if has_reached_monthly_submission_limit(current_app.config['MONTLY_SUBMISSION_LIMIT']):
        limit_message = MONTLY_SUBMISSION_LIMIT_MESSAGE
    else:
        limit_message = None
    return render_template('main.html', limit_message=limit_message)

@main.route('/receive_art', methods=('POST', ))
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

    artpiece = user.make_artpiece(data['title'], data['art'])
    db.session.commit()

    # TODO: handle exceptions
    send_confirmation_email_async(artpiece)

    return jsonify({'success': 'We will send you a confirmation email'}), 201
