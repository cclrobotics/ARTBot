from marshmallow import fields, Schema, post_load, ValidationError
from marshmallow.validate import Length, Regexp
from web.artpiece import Artpiece, has_matching_color_scheme, has_pixels_within_canvas
from web.colors import get_available_color_names
import web.artpiece as artpiece

_ALPHA_NUM_REGEX = r"^[\w\s]+$"

def validate_color_scheme(pixel_art_color_encoding):
    if not has_matching_color_scheme(pixel_art_color_encoding, get_available_color_names()):
        raise ValidationError('Invalid color scheme')

def validate_pixels(pixel_art_color_encoding):
    for color in pixel_art_color_encoding:
        if not has_pixels_within_canvas(pixel_art_color_encoding[color]):
            raise ValidationError('pixel out-of-bounds')

class ArtpieceSchema(Schema):
    title = fields.Str(
            required=True
            , validate=[
                Length(1, 50, error="Art must be named! Resubmit with an awesome title.")
                , Regexp(_ALPHA_NUM_REGEX
                    , error="Title is limited to alpha-numeric characters only")
                ]
            )
    email = fields.Email(required=True, load_only=True)
    art = fields.Dict(
            required=True
            , keys=fields.Str()
            , values=fields.List(fields.Tuple((fields.Int(), fields.Int())))
            , validate=[
                validate_color_scheme
                , validate_pixels
                , Length(1, error="Looks like you forgot to draw something...")
                ]
            )

    @post_load
    def make_artpiece(self, data, many, **kwargs):
        data['title'] = data['title'].strip()
        return data

    class meta:
        strict=True
