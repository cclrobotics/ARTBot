import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import string
from datetime import datetime
import os
from contextlib import contextmanager

from web.database.models import (ArtpieceModel, SubmissionStatus, BacterialColorModel)

def read_args(args):
    if not args: args = {'notebook':False
                        ,'palette':'nunc_8_wellplate_flat'
                        ,'pipette':'P10_Single'
                        }
    NOTEBOOK = args.pop('notebook')
    LABWARE = args #assume unused args are all labware
    return NOTEBOOK, LABWARE

def initiate_environment(SQLALCHEMY_DATABASE_URI = None):
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        if not SQLALCHEMY_DATABASE_URI:
            raise Exception('Database URI expected in env vars or passed explcitly')
    return APP_DIR, SQLALCHEMY_DATABASE_URI

def initiate_sql(SQLALCHEMY_DATABASE_URI):
    SQL_ENGINE = sa.create_engine(SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=SQL_ENGINE)
    return Session

@contextmanager
def session_scope(Session):
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

def add_labware(template_string, labware):
    # replace labware placeholders with the proper Opentrons labware name, as specified in the arguments
    labware['tiprack'] = 'tiprack-200ul' if 'P300' in labware['pipette'] else 'tiprack-10ul'
    
    procedure = template_string.replace('%%PALETTE GOES HERE%%', labware['palette'])
    procedure = procedure.replace('%%PIPETTE GOES HERE%%', labware['pipette'])
    procedure = procedure.replace('%%TIPRACK GOES HERE%%', labware['tiprack'])
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

def make_procedure(artpiece_ids, SQLALCHEMY_DATABASE_URI, num_pieces = 9, option_args = None): 
    NOTEBOOK, LABWARE = read_args(option_args)
    APP_DIR, SQLALCHEMY_DATABASE_URI = initiate_environment(SQLALCHEMY_DATABASE_URI)
    Session = initiate_sql(SQLALCHEMY_DATABASE_URI)

    with session_scope(Session) as session:
        output_msg = []
        
        query_filter = (ArtpieceModel.status == SubmissionStatus.submitted
                       ,ArtpieceModel.confirmed == True
                       )
        if artpiece_ids: query_filter += (ArtpieceModel.id in artpiece_ids,)

        artpieces = (session.query(ArtpieceModel)
                .filter(*query_filter)
                .order_by(ArtpieceModel.submit_date.asc())
                .limit(num_pieces)
                .all())

        if not artpieces:
            output_msg.append('No new art found. All done.')
        else:
            output_msg.append(f'Loaded {len(artpieces)} pieces of art')
            for artpiece in artpieces:
                output_msg.append(f"{artpiece.id}: {artpiece.title}, {artpiece.submit_date}")

            # Get all colors
            colors = session.query(BacterialColorModel).all()

            #Get Python art procedure template
            file_extension = 'ipynb' if NOTEBOOK == True else 'py' #Use Jupyter notbook template or .py template
            with open(os.path.join(APP_DIR,f'ART_TEMPLATE.{file_extension}')) as template_file:
                template_string = template_file.read()

            procedure = add_labware(template_string, LABWARE)
            procedure, canvas_locations = add_canvas_locations(procedure, artpieces)
            procedure = add_pixel_locations(procedure, artpieces)
            procedure = add_color_map(procedure, colors)

            now = datetime.now().strftime("%Y%m%d-%H%M%S")
            unique_file_name = f'ARTISTIC_PROCEDURE_{now}.{file_extension}'
            with open(os.path.join(APP_DIR,'procedures',unique_file_name),'w') as output_file:
                output_file.write(procedure)

            for artpiece in artpieces:
                artpiece.status = SubmissionStatus.processed

            output_msg.append(f'Successfully generated artistic procedure into: ARTBot/robot/procedures/{unique_file_name}')
            output_msg.append('The following slots will be used:')
            output_msg.append('\n'.join([f'Slot {str(canvas_locations[key])}: "{key}"' for key in canvas_locations]))
    return output_msg, f'ARTBot/robot/procedures/{unique_file_name}'
