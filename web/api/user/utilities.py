import os
from PIL import Image
import random
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_current_user
from .artpiece import Artpiece
from .exceptions import InvalidUsage
from web.extensions import cache


#decorator to require admin_acccess for a route
def access_level_required(level):
    try:
        def outer(func):
            @wraps(func)
            def inner(*args, **kwargs):
                if get_current_user().role < level:
                    raise InvalidUsage.forbidden()
                return func(*args, **kwargs)
            return inner
    except TypeError:
        raise TypeError("Specify an access level to use access_level_required decorator")

    return outer


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