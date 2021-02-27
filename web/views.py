#views.py - Maps URLs to backend functions, then returns the results to the appropriate view

from functools import wraps
from flask import (render_template, Blueprint, current_app, request)
from web.extensions import cache, jwt
from .api.user.artpiece import DEFAULT_CANVAS
from .api.user.utilities import get_gallery_images
from .settings import ANNOUNCEMENT

main = Blueprint('main', __name__)

#Home page
@main.route('/', methods=('GET', ))
@main.route('/index', methods=('GET', ))
@cache.cached(timeout=60)
def index():
    return render_template('main.html', canvas_size=DEFAULT_CANVAS, announcement=ANNOUNCEMENT, home_tag=' active', about_tag='')

@main.route('/about',methods=('GET',))
@cache.cached(timeout=60)
def about():
    img_list = get_gallery_images()
    return render_template('about.html', img_list=img_list, home_tag='', about_tag=' active')

@main.route('/print', methods=('GET', ))
def print():
    return render_template('print.html')

@main.route('/art_confirmation', methods=('GET', ))
def art_confirmation():
    args = request.args
    token = args.get('token')
    artpiece_id = args.get('id')

    return render_template(
            'art_confirmation.html', confirmation_token=token, artpiece_id=artpiece_id
            )