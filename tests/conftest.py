import pytest
import os
from flask import current_app
from flask_migrate import upgrade, downgrade
from random import randint
from web.app import create_app
from web.extensions import db

from web.api.user.artpiece.core import create_artpiece
from web.database.models import ArtpieceModel
from web.api.lab_objects.lab_objects import LabObject

### Constants for use in tests ###
VALID_EMAIL = 'valid@mail.com'
VALID_TITLE = 'valid title'
VALID_ART = {'1': [[0,0]], '2': [[1,1]], '3': [[2,2]]}
VALID_CANVAS_SIZE = {'x':26,'y':26}
VALID_PASSWORD = 'ThisIsALongAndValidPassword'
INITIAL_ROLE = 'Artist'
INITIAL_SUPERUSER_ROLE = 'Printer'
INITIAL_PASSWORD_HASH = None

VALID_PLATE = dict()
properties1 = [
        {'name': 'x_radius', 'units': 'mm', 'value':52.5},
        {'name': 'y_radius', 'units': 'mm', 'value':35},
        {'name': 'z_touch_position', 'units': 'frac', 'value':-0.5},
        {'name': 'shape', 'value':'rectangular'}
    ]
VALID_PLATE['ccl_artbot_canvas'] = ('ccl_artbot_canvas','labware', properties1)

properties2 = [
        {'name': 'x_radius', 'units': 'mm', 'value':40},
        {'name': 'y_radius', 'units': 'mm', 'value':40},
        {'name': 'z_touch_position', 'units': 'frac', 'value':0.273},
        {'name': 'shape', 'value':'round'}
    ]
VALID_PLATE['ccl_artbot_canvas_90mm_round'] = ('ccl_artbot_canvas_90mm_round','labware', properties2)

properties3 = [
        {'name': 'x_radius', 'units': 'mm', 'value':25},
        {'name': 'y_radius', 'units': 'mm', 'value':25},
        {'name': 'z_touch_position', 'units': 'frac', 'value':0.273},
        {'name': 'shape', 'value':'round'}
    ]
VALID_PLATE['ccl_artbot_canvas_60mm_round'] = ('ccl_artbot_canvas_60mm_round','labware', properties3)


### Register PyTest marks ###

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "fill_canvas: mark test to run using a completely-filled artpiece"
    )


### Context Management Fixtures ###

@pytest.fixture(scope='session')
def test_app():
    app = create_app()
    app.config.from_object('web.settings.TestingConfig')
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def test_database():
    upgrade()
    yield db
    db.session.remove()
    db.reflect()
    db.drop_all()

@pytest.fixture(scope='function')
def clear_database():
    yield
    db.session.rollback()
    meta = db.metadata
    for table in reversed(meta.sorted_tables): #More idiomatic way to keep default data in DB is preferable
        if table.name != 'bacterial_colors': db.session.execute(table.delete())
    db.session.commit()

@pytest.fixture(scope='session')
def test_directory():
    APP_DIR = current_app.config['APP_DIR']
    path = os.path.join(APP_DIR,'robot/procedures')
    existing_files = os.listdir(path)
    yield path
    for f in os.listdir(path):
        if f not in existing_files:
            os.remove(os.path.join(path, f))

@pytest.fixture(scope="function")
def setup_app(test_app, test_database, clear_database):
    yield


### Application-Specific Fixtures ###

@pytest.fixture(scope='function')
def generate_random_art():
    def random_art(num_colors, xdim, ydim, fill=False):
        art = dict()
        canvas = [[]*ydim]*xdim
        for x in range(xdim):
            for y in range(ydim):
                color = str(randint(fill,num_colors))
                if color != "0":
                    if color not in art:
                        art[color] = [[y,x]]
                    else:
                        art[color].append([y,x])
        return art
    return random_art

@pytest.fixture(scope = 'function', params=[(5,39,26), (5,26,39), (2,50,50)])
def random_test_art_ids(request, test_database, generate_random_art):
    fill = request.node.get_closest_marker('fill_canvas')
    fill = fill.args[0] if fill else False
    
    art_params = request.param
    canvas_size = {'x':art_params[1], 'y':art_params[2]}
    num_artpieces = 9
    artpiece_ids = list()
    for i in range(num_artpieces):
        art = generate_random_art(*art_params, fill)
        artpiece = create_artpiece(VALID_EMAIL + str(i), VALID_TITLE, art, canvas_size)
        artpiece.confirm()
        artpiece_ids.append(artpiece.id)
    test_database.session.commit()
    return artpiece_ids, art_params

@pytest.fixture(scope='function')
def art_from_test_db(request, test_database):
    artpiece_ids = request.node.get_closest_marker('artpieces_ids') or None
    num_pieces = request.node.get_closest_marker('num_pieces') or 9
    
    query_filter = (ArtpieceModel.confirmed == True,)
    if artpiece_ids: query_filter += (ArtpieceModel.id.in_(artpiece_ids),)

    artpieces = (test_database.session.query(ArtpieceModel)
            .filter(*query_filter)
            .order_by(ArtpieceModel.submit_date.asc())
            .limit(num_pieces)
            .all())
    return artpieces

@pytest.fixture(scope='function', params = ['ccl_artbot_canvas',
                                           'ccl_artbot_canvas_90mm_round',
                                           'ccl_artbot_canvas_60mm_round'])
def canvas_object_in_db(request):
    plate_name = request.param
    canvas = LabObject.create_new(*VALID_PLATE[plate_name])
    canvas.save()
    return canvas