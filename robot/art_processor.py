import json
import sqlalchemy as db
import pandas as pd #pandas is overkill, but it makes the database work really really easy, and that's nice
import string
from datetime import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath(os.path.join(basedir, os.pardir, 'ARTBot.db'))
SQL_ENGINE = db.create_engine(SQLALCHEMY_DATABASE_URI)
artpieces = pd.read_sql("SELECT * FROM artpieces WHERE status = 'Submitted'",SQL_ENGINE, parse_dates = ['submit_date'])
artpieces['art'] = artpieces.art.apply(json.loads)

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


#Get JSON template
template_file = open('ART_TEMPLATE.txt')
template_string = template_file.read()
template_file.close()

def make_procedure(artpiece):
    art = artpiece.art
    for color in art:
        art[color] = [well_map(well) for well in art[color]]
    #This works for one canvas. Jinja templating might actually be a better way to do this for multiple canvases
    canvas_string = template_string.replace('%%RED WELLS GO HERE%%',str(art['red'])[1:-1])
    canvas_string = canvas_string.replace('%%BLUE WELLS GO HERE%%', str(art['blue'])[1:-1])
    canvas_string = canvas_string.replace('%%GREEN WELLS GO HERE%%', str(art['green'])[1:-1])

    return canvas_string


canvas_procedures = artpieces.iloc[:1].apply(make_procedure, axis=1)
final_procedure_string = '\n\n'.join(canvas_procedures.tolist())

unique_file_name = 'ARTISTIC_PROCEDURE_%s.py' % datetime.now().strftime("%Y%m%d-%H%M%S")
output_file = open(os.path.join(basedir,'procedures',unique_file_name),'w')
output_file.write(final_procedure_string)
output_file.close()

