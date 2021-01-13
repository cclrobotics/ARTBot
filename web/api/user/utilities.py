import os
from PIL import Image
from .artpiece import Artpiece
from web.extensions import cache
import random

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