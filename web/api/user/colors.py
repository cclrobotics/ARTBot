from flask import g
from marshmallow import fields, Schema, post_dump
from web.database.models import BacterialColorModel

BacterialColor = BacterialColorModel

def get_available_colors():
    return BacterialColor.query.filter(BacterialColor.in_use == True).all()

def get_available_colors_as_dicts():
    return [{'id': color.id, 'name': color.name, 'rgba': color.rgba} for color in
            get_available_colors()]

def get_all_colors():
    return BacterialColor.query.all()

def get_available_color_mapping():
    if not hasattr(g, 'color_mapping'):
        g.color_mapping = {str(color.id): color.rgba for color in get_available_colors()}
    return g.color_mapping
