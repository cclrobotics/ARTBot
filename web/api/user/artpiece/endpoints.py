import os
from flask import (Blueprint, request, current_app, jsonify, send_file, render_template_string)
from flask_jwt_extended import jwt_required
from .core import (validate_and_extract_artpiece_data, create_artpiece,
        has_reached_monthly_submission_limit, guarantee_monthly_submission_limit_not_reached)
from .core import confirm_artpiece as core_confirm_artpiece
from ..email import send_confirmation_email_async
from ..exceptions import InvalidUsage
from ..colors import (get_available_color_mapping, get_available_colors_as_dicts)
from ..utilities import access_level_required
from .artpiece import Artpiece
from .serializers import ArtpieceSchema, PrintableSchema
from web.extensions import db
from web.database.models import SuperUserRole
from web.robot.art_processor import make_procedure

import base64

from web.database.models import ArtpieceModel


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
    confirmation_status = core_confirm_artpiece(artpiece, token)
    if confirmation_status == 'confirmed':
        db.session.commit()

    return jsonify({'data': {'confirmation': {'status': confirmation_status}}}), 200

@artpiece_blueprint.route('/print_jobs', methods=('GET', ))
@jwt_required()
@access_level_required(SuperUserRole.printer)
def get_print_jobs():
    print_jobs = Artpiece.get_printable()
    schema = PrintableSchema(many=True)
    serialized = schema.dumps(print_jobs)

    return jsonify({'data': serialized})

@artpiece_blueprint.route('/procedures/<string:id>', methods=('GET', ))
@jwt_required()
@access_level_required(SuperUserRole.printer)
def get_procedure_file(id):
    
    procedure_file = f'{os.getcwd()}/web/robot/procedures/ARTISTIC_PROCEDURE_{id}'

    return send_file(procedure_file, mimetype='text/plain', as_attachment=True)

@artpiece_blueprint.route('/procedure_request', methods=('POST', ))
@jwt_required()
@access_level_required(SuperUserRole.printer)
def receive_print_request():

    artpiece_ids = request.get_json()['ids']

    msg, procedure_loc = make_procedure(artpiece_ids)

    if procedure_loc:
        unique_id = procedure_loc[1].split('_')[-1]
        procedure_uri = f'/procedures/{unique_id}'
    else:
        procedure_uri = None
        raise InvalidUsage.resource_not_found()
    
    return jsonify({'msg':msg, 'procedure_uri':procedure_uri}), 201
    