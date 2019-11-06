from collections import namedtuple
import json
import datetime as dt
import math
from PIL import Image, ImageDraw
from web.database.models import ArtpieceModel, SubmissionStatus
from web.settings import Config 

Artpiece = ArtpieceModel
_CartesianCoordinates = namedtuple('CartesianCoordinates', ['x', 'y'])
Canvas = _CartesianCoordinates

def make_artpiece(title, email, art):
        submit_date = dt.datetime.now()
        raw_image = decode_to_image(art, Config.COLOR_SCHEME)
        return Artpiece(title=title, email=email, submit_date=submit_date
                , art=art, status=SubmissionStatus.submitted, raw_image=raw_image)

def get_artpiece_by_id(id):
    return Artpiece.get_by_id(id)

def active_submission_count(email):
    return (
            Artpiece.query.filter(
                Artpiece.email == email
                , Artpiece.status == SubmissionStatus.submitted)
            .count()
    )

def total_submission_count_since(date):
    return Artpiece.query.filter(Artpiece.submit_date >= date).count()

def has_matching_color_scheme(pixel_art_color_encoding, allowed_color_scheme):
    for color in pixel_art_color_encoding:
        if color not in allowed_color_scheme:
            return False
    return True

def has_pixels_within_canvas(pixels, canvas_size=Canvas(39, 26)):
    for y, x in pixels:
        if x > canvas_size.x or y > canvas_size.y: #check for negative values?
            return False
    return True
    
def decode_to_image(pixel_art_color_encoding, color_mapping, scale=200):
    canvas_size = Canvas(39, 26)
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
