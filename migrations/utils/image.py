from collections import namedtuple
from PIL import Image, ImageDraw
import math
from typing import Dict, List

Art = Dict[str, List[List[int]]]

Lengths = namedtuple('lengths', ['x', 'y'])
Canvas = Lengths
DEFAULT_CANVAS = Canvas(39, 26)

def decode_art_to_image(pixel_art_color_encoding, color_mapping
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

"""
include colors whose names have been changed
"""
def extend_color_names_to_ids(names_to_ids: Dict) -> Dict:
    names_to_ids['yellow'] = names_to_ids['fluorescent yellow']
    names_to_ids['orange'] = names_to_ids['peach']
    return names_to_ids

"""
replace color names with deprecated names
"""
def replace_color_names(ids_to_names: Dict) -> Dict:
    names_to_ids = {v: k for k, v in ids_to_names.items()}
    yellow_id = names_to_ids['fluorescent yellow']
    orange_id = names_to_ids['peach']
    ids_to_names[yellow_id] = 'yellow'
    ids_to_names[orange_id] = 'orange'
    return ids_to_names

"""
Replaces the art keys with the given new_keys
"""
def migrate_colors(art: Art, new_keys: Dict) -> Art:
    return {new_keys[k]: v for k, v in art.items()}
