from collections import namedtuple
from time import time
import io
import json
import datetime as dt
import math
import re
from PIL import Image, ImageDraw
from slugify import slugify
from flask import current_app
from flask_jwt_extended import create_access_token, decode_token
from web.database.models import ArtpieceModel, SubmissionStatus
from web.api.user.colors import get_available_color_mapping

_CartesianCoordinates = namedtuple('CartesianCoordinates', ['x', 'y'])
Canvas = _CartesianCoordinates
DEFAULT_CANVAS = Canvas(39, 26)

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
        # pixels are given as [y,x]
        for pixel_y, pixel_x in pixel_art_color_encoding[color]:
            origin = (pixel_size[0] * pixel_x, pixel_size[1] * pixel_y)
            far_corner = (pixel_size[0] + origin[0], pixel_size[1] + origin[1])
            draw.rectangle([origin, far_corner], fill=color_mapping[color])

    return (im.tobytes())

def _create_unique_slug(title):
    slug = slugify(title)
    search = f'{slug}#%'
    artpiece_with_slug = (ArtpieceModel.query.filter(
            ArtpieceModel.slug.like(search))
            .order_by(ArtpieceModel.submit_date.desc())
            .first())
    postfix = 1
    if artpiece_with_slug is not None:
        m = re.search(r'\d$', artpiece_with_slug.slug)
        postfix = int(m.group(0)) + 1
    return f'{slug}#{postfix}'


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
        raw_image = _decode_to_image(art, get_available_color_mapping())
        slug = _create_unique_slug(title)
        return cls(
                _Model(slug=slug, title=title, submit_date=submit_date, art=art
                    , status=SubmissionStatus.submitted, raw_image=raw_image
                    , user_id=user_id, confirmed=False)
                .save())

    @classmethod
    def get_by_id(cls, id):
        model = _Model.get_by_id(id)
        return None if model is None else cls(_Model.get_by_id(id))

    @classmethod
    def get_printable(cls):
        model = (
            _Model.query.filter(
            ArtpieceModel.status == SubmissionStatus.submitted
            , ArtpieceModel.confirmed == True)
            .order_by(ArtpieceModel.submit_date.asc())
            .all())
        return model

    @property
    def creator(self):
        from ..user import User
        return User.get_by_id(self._model.user_id)

    def get_image_as_jpg(self, size=(616,414)):
        image = Image.frombytes('RGBX', (616,414), self._model.raw_image)
        if size != (616,414): image = image.resize(size)
        with io.BytesIO() as output:
            image.save(output, format='JPEG')
            image_file = output.getvalue()
        #FIX: (1) This ignores IO stream above
        #     (2) saves to file system without cleaning up after itself
        #     (3) uses hard-coded file location, because I can't get relative reference working
        #     (4) Returns a file URI instead of bytes
        loc = '/usr/src/app/web/static/img/art_designs/' + str(self._model.id) + '.jpg'
        image.save(loc, format='JPEG')
        return loc

    def get_confirmation_token(self, expires_in=60*60*72):
        return create_access_token(
                identity = {'confirm_artpiece': self._model.id, 'exp': time() + expires_in},
                expires_delta = dt.timedelta(seconds = expires_in)
                )

    def verify_confirmation_token(self, token):
        id = decode_token(token, allow_expired=False)['sub']['confirm_artpiece']
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
