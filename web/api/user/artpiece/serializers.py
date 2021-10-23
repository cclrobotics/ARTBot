from marshmallow import (fields, Schema, pre_load, post_dump, validates)
from marshmallow.validate import (Length, Regexp)
from .validators import (validate_art_content_length, validate_color_keys, validate_pixels,
        validate_title)
from ...file_manager import file_manager

_fm = file_manager()

class ArtpieceSchema(Schema):
    title = fields.Str(missing=None)
    email = fields.Email(required=True, load_only=True)
    art = fields.Dict(
            missing=None
            , keys=fields.Str()
            , values=fields.List(fields.Tuple((fields.Int(), fields.Int())))
            )

    def __init__(self, valid_color_keys, many=False):
        Schema.__init__(self, many=many)
        self._valid_color_keys = valid_color_keys

    @validates('title')
    def _validate_title_field(self, title):
        validate_title(title)

    @validates('art')
    def _validate_art_field(self, art):
        validate_art_content_length(art)
        validate_color_keys(art, self._valid_color_keys)
        validate_pixels(art)

    @pre_load
    def strip_title(self, in_data, **kwargs):
        title = in_data['title'] if in_data else None
        if title is not None:
            in_data['title'] = title.strip()
        return in_data

    class meta:
        strict=True

class PrintableSchema(Schema):
    id = fields.Int()
    title = fields.Str(missing=None)
    user_id = fields.Int()
    submit_date = fields.DateTime()
    status = fields.Str()
    art = fields.Dict(
            missing=None
            , keys=fields.Str()
            , values=fields.List(fields.Tuple((fields.Int(), fields.Int())))
            )
    img_uri = fields.Function(lambda obj: _fm.get_file_url(f'{obj.slug}_{int(obj.submit_date.timestamp()*1000)}.jpg'))

    class Meta:
        ordered = True