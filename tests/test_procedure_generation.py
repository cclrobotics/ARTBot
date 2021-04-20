import pytest
import os
from random import randint
from difflib import ndiff
from flask import current_app
from web.robot.art_processor import (optimize_print_order,
                                     euclidean_distance,
                                     make_procedure
)
from web.api.user.artpiece.core import create_artpiece
from .test_user_api import VALID_EMAIL, VALID_TITLE

@pytest.fixture(scope="function")
def setup_app(test_app, test_database, clear_database):
    yield

def generate_random_art(num_colors, xdim, ydim):
    art = dict()
    canvas = [[]*ydim]*xdim
    for x in range(xdim - 1):
        for y in range(ydim - 1):
            color = str(randint(0,num_colors))
            if color != "0":
                if color not in art:
                    art[color] = [[x,y]]
                else:
                    art[color].append([x,y])
    return art  

#From a known artpiece, ensure that the optimum path is found
@pytest.mark.parametrize('unordered_path', [[[0, 0], [25, 0], [0, 1], [25, 1]]])
def test_optimize_print_order_strong(unordered_path):  
    ordered_path = optimize_print_order(unordered_path)
    assert ordered_path == [[0, 0], [0, 1], [25, 1], [25, 0]]

#Generate a random artpiece and ensure each optimized print path is equal or shorter than unoptimized
@pytest.mark.parametrize('art_params', [(5,39,26), (1,50,50), (10,25,25)])
def test_optimize_print_order_weak(art_params):
    def calc_path_distance(path):
        path_distance = 0
        for point_num in range(len(path) - 1):
            path_distance += euclidean_distance(path[point_num], path[point_num + 1])
        return path_distance

    unordered_art = generate_random_art(*art_params)
    for color in unordered_art:
        unordered_path = unordered_art[color]
        unordered_distance = calc_path_distance(unordered_path)
        ordered_path = optimize_print_order(unordered_path)
        assert calc_path_distance(ordered_path) <= unordered_distance

@pytest.mark.usefixtures('setup_app')
@pytest.mark.parametrize('art_params', [(5,39,26), (2,50,50)])
@pytest.mark.parametrize('num_artpieces', [1,2,9])
def test_generate_procedure(art_params, num_artpieces, test_database, test_directory):
    """Tests that a procedure is made and that it only differs from template on intended lines
       Does not currently test if replacements are valid or if output is functional   
    """

    artpiece_ids = list()
    for i in range(num_artpieces):
        art = generate_random_art(*art_params)
        artpiece = create_artpiece(VALID_EMAIL + str(i), VALID_TITLE, art)
        artpiece.confirm()
        artpiece_ids.append(artpiece.id)
    test_database.session.commit()
    
    status, procedure_path = make_procedure(artpiece_ids,
                                            test_database.engine.url
    )
    assert procedure_path is not None
    
    template_dir = procedure_path[0].split('/procedures')[0]
    with open(os.path.join(template_dir,'ART_TEMPLATE.py')) as template_file:
                template_string = template_file.read()
    with open(os.path.join(*procedure_path)) as output_file:
                output_string = output_file.read()
    diffs = ndiff(template_string.splitlines(1), output_string.splitlines(1))
    
    for diff in diffs:
        if diff[0] == '-':
            assert '%%' in diff