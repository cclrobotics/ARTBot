import os
from PIL import Image
from .artpiece import Artpiece
from web.extensions import cache, jwt
import random

from flask_jwt_extended import jwt_required, create_access_token, get_current_user
from functools import wraps

@cache.memoize(timeout=3600)
def get_image_description(image_path):
    with Image.open(image_path) as image:
        # Exif ID 270 = ImageDescription
        return image.getexif().get(270)

"""
Return a list of images in the 'gallery' folder and their descriptions
Output is list of tuples (image_location, image_description)
    output list is in random order for random display order every time
"""
def get_gallery_images():
    internal_path_prefix = './web'
    public_gallery_path = '/static/img/gallery/'

    image_paths = [
        public_gallery_path + filename
        for filename in os.listdir(internal_path_prefix + public_gallery_path)
    ]

    image_descriptions = list()
    for image_path in image_paths:
        this_image_description = get_image_description(internal_path_prefix + image_path)
        image_descriptions.append(this_image_description)

    image_metadata = list(zip(image_paths, image_descriptions))
    random.shuffle(image_metadata)

    return image_metadata

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    user = jwt_data['sub']
    return user

def admin_required(level):
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if get_current_user() == 'test':
                return jsonify({'msg': 'admin access required',
                                'user': get_current_user()}), 403
            return func(*args, **kwargs)
        return inner
    return outer