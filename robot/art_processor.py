import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import string
from datetime import datetime
import os, argparse
from contextlib import contextmanager

from .custom_artbot_labware import custom_plates
from web.database.models import ArtpieceModel, SubmissionStatus

parser = argparse.ArgumentParser()
parser.add_argument('--notebook'
                    ,action='store_true'
                    ,help='Set this flag to output to a Jupyter Notebook instead of a .py file'
                    )
parser.add_argument('--wellplate'
        , choices=custom_plates.keys()
        , help='The plate type to use'
        )
args = parser.parse_args()
NOTEBOOK = args.notebook
WELLPLATE_TYPE = args.wellplate or 'nunc_8_wellplate_flat'
grid = custom_plates[WELLPLATE_TYPE]['grid']
wellplate_grid_size = grid[0]*grid[1]

APP_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
DB_NAME = 'ARTBot.db'
# Put the db file in project root
DB_PATH = os.path.join(PROJECT_ROOT, DB_NAME)
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///{0}'.format(DB_PATH))

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

def well_map(well):
    map = dict(zip(range(26), string.ascii_uppercase))
    letter = map[well[0]]
    number = well[1] + 1
    return letter + str(number)

# BUG: overwrites locations if same title
def get_canvas_locations(artpieces):
    # Lists slots that should typically be available
    def canvas_slot_generator():
        for slot in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            yield str(slot)
    get_canvas_slot = canvas_slot_generator()

    return dict(zip([artpiece.title for artpiece in artpieces], get_canvas_slot))

def add_canvas_locations(template_string, canvas_locations):
    # write where canvas plates are to be placed into code
    return template_string.replace('%%CANVAS LOCATIONS GO HERE%%', str(canvas_locations))

def get_pixels_by_color(artpieces):
    # write where to draw pixels on each plate into code. Listed by color to reduce contamination
    pixels_by_color = dict()
    for artpiece in artpieces:
        for color in artpiece.art:
            if color not in pixels_by_color:
                pixels_by_color[color] = dict()
            pixels_by_color[color][artpiece.title] = [well_map(pixel) for pixel in artpiece.art[color]]
    return pixels_by_color

def add_pixel_locations(template_string, pixels_by_color):
    return template_string.replace('%%PIXELS GO HERE%%', str(pixels_by_color))

def add_wellplate_type(template_string, wellplate_type):
    return template_string.replace('%%WELLPLATE TYPE GO HERE%%', "'"+wellplate_type+"'")

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

        #Get Python art procedure template
        file_extension = 'ipynb' if NOTEBOOK == True else 'py' #Use Jupyter notbook template or .py template
        with open(os.path.join(APP_DIR,f'ART_TEMPLATE.{file_extension}')) as template_file:
            procedure = template_file.read()

        canvas_locations = get_canvas_locations(artpieces)
        pixels_by_color = get_pixels_by_color(artpieces)
        assert len(pixels_by_color) < wellplate_grid_size, 'More colors than wells'

        procedure = add_canvas_locations(procedure, canvas_locations)
        procedure = add_pixel_locations(procedure, pixels_by_color)
        procedure = add_wellplate_type(procedure, WELLPLATE_TYPE)

        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        unique_file_name = f'ARTISTIC_PROCEDURE_{now}.{file_extension}'
        with open(os.path.join(APP_DIR,'procedures',unique_file_name),'w') as output_file:
            output_file.write(procedure)

        for artpiece in artpieces:
            artpiece.status = SubmissionStatus.processing

        print(('Successfully generated artistic procedure into: '
            f'ARTBot/robot/procedures/{unique_file_name}'))
        print('The following slots will be used:')
        print('\n'.join(
                [f'Slot {str(canvas_locations[key])}: "{key}"' for key in canvas_locations]))
