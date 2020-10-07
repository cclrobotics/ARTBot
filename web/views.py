#views.py - Maps URLs to backend functions, then returns the results to the appropriate view

from flask import (render_template, Blueprint, current_app, request)
from .api.user.artpiece import DEFAULT_CANVAS
from .api.user.utilities import get_gallery_images
from .settings import ANNOUNCEMENT

main = Blueprint('main', __name__)

#Home page
@main.route('/', methods=('GET', ))
@main.route('/index', methods=('GET', ))
def index():
    return render_template('main.html', canvas_size=DEFAULT_CANVAS, announcement=ANNOUNCEMENT)

@main.route('/about',methods=('GET',))
def about():
    img_list = get_gallery_images()
    return render_template('about.html', img_list=img_list)

@main.route('/art_confirmation', methods=('GET', ))
def art_confirmation():
    args = request.args
    token = args.get('token')
    artpiece_id = args.get('id')

    return render_template(
            'art_confirmation.html', confirmation_token=token, artpiece_id=artpiece_id
            )
