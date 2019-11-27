import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import string
from datetime import datetime
import os, argparse
from contextlib import contextmanager

from web.database.models import ArtpieceModel, SubmissionStatus

parser = argparse.ArgumentParser()
parser.add_argument('--notebook'
                    ,action='store_true'
                    ,help='Set this flag to output to a Jupyter Notebook instead of a .py file'
                    )
NOTEBOOK = parser.parse_args().notebook

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
def add_canvas_locations(template_string, artpieces):
    # write where canvas plates are to be placed into code
    canvas_locations = dict(zip([artpiece.title for artpiece in artpieces], get_canvas_slot))
    procedure = template_string.replace('%%CANVAS LOCATIONS GO HERE%%', str(canvas_locations))

    return procedure, canvas_locations


def add_pixel_locations(template_string, artpieces):
    # write where to draw pixels on each plate into code. Listed by color to reduce contamination
    pixels_by_color = dict()
    for artpiece in artpieces:
        for color in artpiece.art:
            if color not in pixels_by_color:
                pixels_by_color[color] = dict()
            pixels_by_color[color][artpiece.title] = [well_map(pixel) for pixel in artpiece.art[color]]
    procedure = template_string.replace('%%PIXELS GO HERE%%', str(pixels_by_color))

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

        #Get Python art procedure template
        file_extension = 'ipynb' if NOTEBOOK == True else 'py' #Use Jupyter notbook template or .py template
        with open(os.path.join(APP_DIR,f'ART_TEMPLATE.{file_extension}')) as template_file:
            template_string = template_file.read()

        procedure, canvas_locations = add_canvas_locations(template_string, artpieces)

        procedure = add_pixel_locations(procedure, artpieces)


        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        unique_file_name = f'ARTISTIC_PROCEDURE_{now}.{file_extension}'
        with open(os.path.join(APP_DIR,'procedures',unique_file_name),'w') as output_file:
            output_file.write(procedure)

        updated_records = session.query(ArtpieceModel).filter(ArtpieceModel.id.in_([artpiece.id for artpiece in artpieces]))
        for record in updated_records:
            record.status = SubmissionStatus.processed

        print(f'Successfully generated artistic procedure into: ARTBot/robot/procedures/{unique_file_name}')
        print('The following slots will be used:')
        print('\n'.join([f'Slot {str(canvas_locations[key])}: "{key}"' for key in canvas_locations]))
