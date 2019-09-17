import os
import json
import sqlalchemy as db
import pandas as pd
import math
from PIL import Image, ImageDraw

basedir = os.path.abspath(os.path.dirname(__file__))

def rebuild_art(art):
    colors = {
        'pink': (255,192,203,1)
        ,'blue': (0,0,255,1)
        ,'teal': (0,128,128,1)
        ,'orange': (255,165,0,1)
        ,'yellow': (255,255,0,1)
    }

    scale = 40 * 5
    num_pixels = (39, 26)
    ratio = (3,2)
    pixel_size = (ratio[0] * scale / num_pixels[0]
                 ,ratio[1] * scale / num_pixels[1])
    total_size = (math.ceil(ratio[0] * scale + pixel_size[0])
                 ,math.ceil(ratio[1] * scale + pixel_size[1]))

    im = Image.new('RGBA',total_size,(255,255,255,1))
    draw = ImageDraw.Draw(im)

    for art_color in art:
        for pixel in art[art_color]:
            origin = [pixel_size[0] * pixel[1] , pixel_size[1] * pixel[0]] #pixels are given (y,x)
            far_corner = [pixel_size[0] + origin[0], pixel_size[1] + origin[1]]
            draw.rectangle(origin + far_corner,  fill = colors[art_color])

    return im