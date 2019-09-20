import json
import sqlalchemy as db
import pandas as pd #pandas is overkill, but it makes the database work really really easy, and that's nice
import string
from datetime import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath(os.path.join(basedir, os.pardir, 'ARTBot.db'))
SQL_ENGINE = db.create_engine(SQLALCHEMY_DATABASE_URI)

num_pieces = 0
while num_pieces not in range(1,10):
    try:
        num_pieces = int(input("How much art? (1-9)"))
    except:
        num_pieces = 0
query = f"""SELECT * FROM artpieces
           WHERE status = 'Submitted'
           ORDER BY submit_date ASC
           LIMIT {num_pieces}
        """

artpieces = pd.read_sql(query, SQL_ENGINE, parse_dates = ['submit_date'])
artpieces['art'] = artpieces.art.apply(json.loads)

print(f'Loaded {len(artpieces)} pieces of art')
print(artpieces[['title','email','submit_date']])

#Lists slots that should typically be available
def canvas_slot_generator():
    for slot in [1,2,3,4,5,6,7,8,9]:
        yield str(slot)
get_canvas_slot = canvas_slot_generator()

def well_map(well):
    map = dict(zip(range(26), string.ascii_uppercase))
    letter = map[well[0]]
    number = well[1] + 1
    return letter + str(number)

def add_canvas_locations(template_string, artpieces):
    #write where canvas plates are to be placed into code
    canvas_locations = dict(zip(artpieces.title,get_canvas_slot))
    procedure = template_string.replace('%%CANVAS LOCATIONS GO HERE%%', str(canvas_locations))

    return procedure

def add_pixel_locations(template_string, artpieces):
    #write where to draw pixels on each plate into code. Listed by color to reduce
    pixels_by_color = dict()
    for index, artpiece in artpieces.iterrows():
        for color in artpiece.art:
            if color not in pixels_by_color:
                pixels_by_color[color] = dict()
            pixels_by_color[color][artpiece.title] = artpiece.art[color]
    procedure = procedure.replace('%%PIXELS GO HERE%%', str(pixels_by_color))

    return procedure


#Get Python art procedure template
template_file = open('ART_TEMPLATE.txt')
template_string = template_file.read()
template_file.close()


procedure = add_canvas_locations(template_string, artpieces)

procedure = add_pixel_locations(procedure, artpieces)


now = datetime.now().strftime("%Y%m%d-%H%M%S")
unique_file_name = f'ARTISTIC_PROCEDURE_{now}.py'
output_file = open(os.path.join(basedir,'procedures',unique_file_name),'w')
output_file.write(procedure)
output_file.close()

