from marshmallow import fields, Schema, post_load, ValidationError
from marshmallow.validate import Length, Regexp
from web.artpiece import Artpiece, has_matching_color_scheme, has_pixels_within_canvas
from web.settings import Config 
import web.artpiece as artpiece

COLOR_SCHEME = Config.COLOR_SCHEME
_ALPHA_NUM_REGEX = r"^[a-zA-Z0-9]+$"

def validate_color_scheme(pixel_art_color_encoding):
    if not has_matching_color_scheme(pixel_art_color_encoding, COLOR_SCHEME.keys()):
        raise ValidationError('Invalid color scheme')

def validate_pixels(pixel_art_color_encoding):
    for color in pixel_art_color_encoding:
        if not has_pixels_within_canvas(pixel_art_color_encoding[color]):
            raise ValidationError('pixel out-of-bounds')

class ArtpieceSchema(Schema):
    title = fields.Str(
            required=True
            , validate=[Length(1, 50), Regexp(_ALPHA_NUM_REGEX)]
            )
    email = fields.Email(required=True)
    art = fields.Dict(
            required=True
            , keys=fields.Str()
            , values=fields.List(fields.Tuple((fields.Int(), fields.Int())))
            , validate=[validate_color_scheme, validate_pixels]
            )

    @post_load
    def make_artpiece(self, data, many, **kwargs):
        return artpiece.make_artpiece(**data)

    class meta:
        strict=True
