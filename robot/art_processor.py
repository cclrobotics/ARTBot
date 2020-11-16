import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import string
from datetime import datetime
import os, argparse
from contextlib import contextmanager

from web.database.models import (ArtpieceModel, SubmissionStatus, BacterialColorModel)

parser = argparse.ArgumentParser()
parser.add_argument('--notebook'
                    ,action='store_true'
                    ,help='Set this flag to output to a Jupyter Notebook instead of a .py file'
                    )
parser.add_argument('--palette', '-pa'
                    ,default='nunc_8_wellplate_flat'
                    ,help='Optional argument to specify the kind of labware to use as the palette plate. Use Opentrons standard names.'
                    )
parser.add_argument('--pipette', '-pi'
                    ,default='P10_Single'
                    ,help='Optional argument to specify the pipette type. Use Opentrons standard names.'
                    )
args = parser.parse_args()
NOTEBOOK = args.notebook
LABWARE = {'palette':args.palette,'pipette':args.pipette}

APP_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
if not SQLALCHEMY_DATABASE_URI:
    SQLALCHEMY_DATABASE_URI = input('Enter Database Url: ')
SQL_ENGINE = sa.create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=SQL_ENGINE)

@contextmanager
def session_scope():
    """Provide transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# Lists slots that should typically be available
def canvas_slot_generator():
    for slot in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        yield str(slot)
get_canvas_slot = canvas_slot_generator()

def well_map(well):
    map = dict(zip(range(26), string.ascii_uppercase))
    letter = map[well[0]]
    number = well[1] + 1
    return letter + str(number)


# BUG: overwrites locations if same title
def plate_location_map(coord):
    x_wellspacing = 105 / 38
    y_wellspacing = 70 / 25
    x_max_mm = 52.5
    y_max_mm = 35
    well_radius = 35

    x = (x_wellspacing * coord[1] - x_max_mm) / well_radius
    y = (y_wellspacing * -coord[0] + y_max_mm) / well_radius

    return x, y

def add_labware(template_string, **kwargs):
    # replace labware placeholders with the proper Opentrons labware name, as specified in the arguments
    tiprack = 'tiprack-200ul' if 'P300' in pipette else 'tiprack-10ul'
    
    procedure = template_string.replace('%%PALETTE GOES HERE%%', palette)
    procedure = procedure.replace('%%PIPETTE GOES HERE%%', pipette])
    procedure = procedure.replace('%%TIPRACK GOES HERE%%', tiprack)
    return procedure

def add_canvas_locations(template_string, artpieces):
    # write where canvas plates are to be placed into code
    canvas_locations = dict(zip([artpiece.slug for artpiece in artpieces], get_canvas_slot))
    procedure = template_string.replace('%%CANVAS LOCATIONS GO HERE%%', str(canvas_locations))
    return procedure, canvas_locations

def add_pixel_locations(template_string, artpieces):
    # write where to draw pixels on each plate into code. Listed by color to reduce contamination
    pixels_by_color = dict()
    for artpiece in artpieces:
        for color in artpiece.art:
            if color not in pixels_by_color:
                pixels_by_color[color] = dict()
            pixels_by_color[color][artpiece.slug] = [plate_location_map(pixel) for pixel in artpiece.art[color]]
    procedure = template_string.replace('%%PIXELS GO HERE%%', str(pixels_by_color))
    return procedure

def add_color_map(template_string, colors):
    color_map = {str(color.id): color.name for color in colors}
    procedure = template_string.replace('%%COLORS GO HERE%%', str(color_map))
    return procedure

num_pieces = 0
while num_pieces not in range(1,10):
    try:
        num_pieces = int(input("How much art? (1-9) "))
    except:
        num_pieces = 0

with session_scope() as session:
    artpieces = (session.query(ArtpieceModel).filter(
            ArtpieceModel.status == SubmissionStatus.submitted
            , ArtpieceModel.confirmed == True)
            .order_by(ArtpieceModel.submit_date.asc())
            .limit(num_pieces)
            .all())

    if not artpieces:
        print('No new art found. All done.')
    else:
        print(f'Loaded {len(artpieces)} pieces of art')
        for artpiece in artpieces:
            print(f"{artpiece.id}: {artpiece.title}, {artpiece.submit_date}")

        # Get all colors
        colors = session.query(BacterialColorModel).all()

        #Get Python art procedure template
        file_extension = 'ipynb' if NOTEBOOK == True else 'py' #Use Jupyter notbook template or .py template
        with open(os.path.join(APP_DIR,f'ART_TEMPLATE.{file_extension}')) as template_file:
            template_string = template_file.read()

        procedure = add_labware(template_string, **LABWARE)
        procedure, canvas_locations = add_canvas_locations(procedure, artpieces)
        procedure = add_pixel_locations(procedure, artpieces)
        procedure = add_color_map(procedure, colors)

        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        unique_file_name = f'ARTISTIC_PROCEDURE_{now}.{file_extension}'
        with open(os.path.join(APP_DIR,'procedures',unique_file_name),'w') as output_file:
            output_file.write(procedure)

        for artpiece in artpieces:
            artpiece.status = SubmissionStatus.processed

        print(f'Successfully generated artistic procedure into: ARTBot/robot/procedures/{unique_file_name}')
        print('The following slots will be used:')
        print('\n'.join([f'Slot {str(canvas_locations[key])}: "{key}"' for key in canvas_locations]))
