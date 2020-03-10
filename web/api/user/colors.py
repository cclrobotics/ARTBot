from marshmallow import fields, Schema, post_dump
from web.database.models import BacterialColorModel

BacterialColor = BacterialColorModel

def get_available_colors():
    return BacterialColor.query.filter(BacterialColor.in_use == True).all()

def get_all_colors():
    return BacterialColor.query.all()

class BacterialColorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    rgba = fields.Tuple((fields.Int(), fields.Int(), fields.Int(), fields.Int()), dump_only=True)

color_schema = BacterialColorSchema(many=True)
