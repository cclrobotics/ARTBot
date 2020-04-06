from flask import (Blueprint, request, current_app, jsonify)
from .core import (validate_and_extract_artpiece_data, create_artpiece,
        has_reached_monthly_submission_limit, guarantee_monthly_submission_limit_not_reached)
from ..email import send_confirmation_email_async
from ..exceptions import InvalidUsage
from ..colors import (get_available_color_mapping, get_available_colors_as_dicts)
from .artpiece import Artpiece
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
                    , 'bacterial_colors': get_available_colors_as_dicts()
                }
                , 'data': None
            }), 200

@artpiece_blueprint.route('/artpieces', methods=('POST', ))
def receive_art():
    monthly_limit = current_app.config['MONTLY_SUBMISSION_LIMIT']
    guarantee_monthly_submission_limit_not_reached(monthly_limit)

    email, title, art = validate_and_extract_artpiece_data(request.get_json()
            , get_available_color_mapping().keys())

    artpiece = create_artpiece(email, title, art)
    db.session.commit()

    send_confirmation_email_async(artpiece)

    return jsonify({'data': None}), 201

@artpiece_blueprint.route('/artpieces/<int:id>/confirmation/<token>', methods=('PUT', ))
def confirm_artpiece(id, token):
    artpiece = Artpiece.get_by_id(id)
    confirmation_status = confirm_artpiece(artpiece, token)
    if confirmation_status == 'confirmed':
        db.session.commit()

    return jsonify({'data': {'confirmation': {'status': confirmation_status}}}), 200
