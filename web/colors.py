from flask import g
from web.database.models import BacterialColorModel

BacterialColor = BacterialColorModel

def get_available_color_scheme():
    if not hasattr(g, 'color_scheme'):
        g.color_scheme = {color.name: color.rgba for color in get_available_colors()}
    return g.color_scheme

def get_available_colors():
    return BacterialColor.query.filter(BacterialColor.in_use == True).all()

def get_available_color_names():
    return get_available_color_scheme().keys()
