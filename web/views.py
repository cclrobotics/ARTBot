#views.py - Maps URLs to backend functions, then returns the results to the appropriate view

from flask import (render_template, Blueprint, request, current_app, jsonify)
from marshmallow import ValidationError
from web.serializers import ArtpieceSchema
from web.utilities import (sendConfirmationEmailToUser
                        , has_reached_monthly_submission_limit
                        , has_active_submission
                        , pull_picture)
from web.exceptions import (error_template, InvalidUsage, MONTLY_SUBMISSION_LIMIT_MESSAGE)

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
        artpiece = ArtpieceSchema().load(request.get_json())
    except ValidationError as err:
        raise InvalidUsage(**error_template(err.messages))

    if has_active_submission(artpiece.email):
        raise InvalidUsage.reached_user_limit()

    artpiece.save()

    # TODO: handle exceptions
    sendConfirmationEmailToUser(artpiece)

    return jsonify({'success': 'We will send you a confirmation email'}), 201
