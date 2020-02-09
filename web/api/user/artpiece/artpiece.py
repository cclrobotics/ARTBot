from collections import namedtuple
from time import time
import jwt
import io
import json
import datetime as dt
import math
from PIL import Image, ImageDraw
from flask import current_app
from web.database.models import ArtpieceModel, SubmissionStatus
from web.settings import Config


_CartesianCoordinates = namedtuple('CartesianCoordinates', ['x', 'y'])
Canvas = _CartesianCoordinates
DEFAULT_CANVAS = Canvas(39, 26)

def has_matching_color_scheme(pixel_art_color_encoding, allowed_color_scheme):
    for color in pixel_art_color_encoding:
        if color not in allowed_color_scheme:
            return False
    return True

def has_pixels_within_canvas(pixels, canvas_size=DEFAULT_CANVAS):
    for y, x in pixels:
        if x > canvas_size.x or y > canvas_size.y: #check for negative values?
            return False
    return True

def _decode_to_image(pixel_art_color_encoding, color_mapping
    , canvas_size=DEFAULT_CANVAS, scale=200):
    ratio = (3, 2)
    pixel_size = (ratio[0] * scale / canvas_size.x
                 , ratio[1] * scale / canvas_size.y)
    total_size = (math.ceil(ratio[0] * scale + pixel_size[0])
                 , math.ceil(ratio[1] * scale + pixel_size[1]))
    im = Image.new('RGBA',total_size,(255,255,255,1))
    draw = ImageDraw.Draw(im)

    for color in pixel_art_color_encoding:
        for pixel_y, pixel_x in pixel_art_color_encoding[color]:
            origin = (pixel_size[0] * pixel_x, pixel_size[1] * pixel_y) #pixels are given (y,x)
            far_corner = (pixel_size[0] + origin[0], pixel_size[1] + origin[1])
            draw.rectangle([origin, far_corner], fill=color_mapping[color])

    return (im.tobytes())

_Model = ArtpieceModel

class Artpiece():
    def __init__(self, model):
        self._model = model
        self._model_id = model.id

    def refresh(self):
        self._model = _Model.get_by_id(self._model_id)

    @classmethod
    def create(cls, user_id, title, art):
        submit_date = dt.datetime.now()
        raw_image = _decode_to_image(art, Config.COLOR_SCHEME)
        return cls(
                _Model(title=title, submit_date=submit_date, art=art
                    , status=SubmissionStatus.submitted, raw_image=raw_image
                    , user_id=user_id, confirmed=False)
                .save())

    @classmethod
    def get_by_id(cls, id):
        model = _Model.get_by_id(id)
        return None if model is None else cls(_Model.get_by_id(id))

    @property
    def creator(self):
        from ..user import User
        return User.get_by_id(self._model.user_id)

    def get_image_as_jpg(self):
        image = Image.frombytes('RGBX', (616, 414), self._model.raw_image)
        with io.BytesIO() as output:
            image.save(output, format='JPEG')
            image_file = output.getvalue()
        return image_file

    def get_confirmation_token(self, expires_in=60*60*72):
        return jwt.encode(
                {'confirm_artpiece': self._model.id, 'exp': time() + expires_in}
                , current_app.config['JWT_SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def verify_confirmation_token(self, token):
        id = jwt.decode(token, current_app.config['JWT_SECRET_KEY']
                , algorithms=['HS256'])['confirm_artpiece']
        if self._model_id != id:
            raise TokenIDMismatchError()

    def confirm(self):
        self._model.confirmed = True

    def is_confirmed(self):
        return self._model.confirmed

    @property
    def title(self):
        return self._model.title

    @property
    def id(self):
        return self._model_id

    @staticmethod
    def total_submission_count_since(date):
        return _Model.query.filter(_Model.submit_date >= date).count()

class TokenIDMismatchError(Exception):
    """ Artpiece id from token does not match """
    pass
