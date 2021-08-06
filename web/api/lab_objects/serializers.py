from marshmallow import (fields, Schema, post_load, EXCLUDE)
from numbers import Number


class LabObjectPropertySchema(Schema):
    name = fields.Str(required=True)
    value = fields.Field(required=True)
    units = fields.Str(required=False)

    def __init__(self, many=False):
        Schema.__init__(self, many=many)

    class meta:
        strict=True