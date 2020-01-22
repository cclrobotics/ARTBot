#views.py - Maps URLs to backend functions, then returns the results to the appropriate view

from flask import (render_template, Blueprint, current_app, request)
from sqlalchemy.exc import DBAPIError
from .api.user.utilities import has_reached_monthly_submission_limit
from .api.user.exceptions import MONTLY_SUBMISSION_LIMIT_MESSAGE
from .api.user.artpiece import DEFAULT_CANVAS

main = Blueprint('main', __name__)

#Home page
@main.route('/', methods=('GET', ))
@main.route('/index', methods=('GET', ))
def index():
    limit_message = None
    try:
        if has_reached_monthly_submission_limit(current_app.config['MONTLY_SUBMISSION_LIMIT']):
            limit_message = MONTLY_SUBMISSION_LIMIT_MESSAGE
    except DBAPIError:
        pass
    return render_template('main.html', limit_message=limit_message, canvas_size=DEFAULT_CANVAS)


@main.route('/art_confirmation', methods=('GET', ))
def art_confirmation():
    args = request.args
    token = args.get('token')
    artpiece_id = args.get('id')

    return render_template(
            'art_confirmation.html', confirmation_token=token, artpiece_id=artpiece_id
            )
