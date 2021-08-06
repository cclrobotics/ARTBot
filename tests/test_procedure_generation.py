from flask.globals import request
import pytest
import os
import math
from difflib import ndiff
from flask import current_app
from web.robot.art_processor import (optimize_print_order,
                                     euclidean_distance,
                                     plate_location_map,
                                     make_procedure
)

#Scaling tests setup fixture
@pytest.fixture(scope='function')
def art_dimensions(canvas_object_in_db, art_from_test_db):
    artpiece = art_from_test_db[0]
    
    canvas = canvas_object_in_db

    #All this to get the grid size. Only works with full canvas.
    #Rewrite to one line once art reports its own grid size
    grid_size = [0,0]
    for color in artpiece.art:
        for pixel in artpiece.art[color]:
            if pixel[1] > grid_size[0]: grid_size[0] = pixel[1]
            if pixel[0] > grid_size[1]: grid_size[1] = pixel[0]

    all_plate_positions = list()
    all_pixels = list()
    for color in artpiece.art:
        for pixel in artpiece.art[color]:
            plate_position = plate_location_map(pixel, canvas, grid_size)
            all_plate_positions.append(plate_position)
            all_pixels.append(pixel)
    return all_plate_positions, all_pixels, canvas, grid_size



#From a known artpiece, ensure that the optimum path is found
@pytest.mark.parametrize('unordered_path', [[[0, 0], [25, 0], [0, 1], [25, 1]]])
def test_optimize_print_order_strong(unordered_path):  
    ordered_path = optimize_print_order(unordered_path)
    assert ordered_path == [[0, 0], [0, 1], [25, 1], [25, 0]]

#Generate a random artpiece and ensure each optimized print path is equal or shorter than unoptimized
@pytest.mark.parametrize('art_params', [(5,39,26), (1,50,50), (10,25,25)])
def test_optimize_print_order_weak(art_params, generate_random_art):
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

@pytest.mark.usefixtures('test_app', 'clear_database')
@pytest.mark.parametrize('num_artpieces', [1,2,9])
def test_generate_procedure(random_test_art_ids, num_artpieces, canvas_object_in_db, test_database):
    """Tests that a procedure is made and that it only differs from template on intended lines
       Does not currently test if replacements are valid or if output is functional   
    """
    artpiece_ids, art_params = random_test_art_ids
    artpiece_ids = artpiece_ids[:num_artpieces]
    print(random_test_art_ids[0], artpiece_ids)
    status, procedure_path = make_procedure(artpiece_ids,
                                            test_database.engine.url,
                                            option_args={'notebook':False
                                                        ,'palette':'corning_96_wellplate_360ul_flat'
                                                        ,'pipette':'p300_single'
                                                        ,'canvas': canvas_object_in_db.name
                                                        }
    )
    print(status)
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


@pytest.mark.usefixtures('setup_app', 'random_test_art_ids')
@pytest.mark.fill_canvas(True)
def test_all_points_in_bounds(art_dimensions):
    all_plate_positions, all_pixels, canvas, grid_size = art_dimensions
    
    canvas_aspect_ratio = canvas.x_radius_mm / canvas.y_radius_mm
    for point in all_plate_positions:
        if canvas.shape == 'round':
            if point[1] != 0:
                angle = math.atan(point[0]/point[1])
            else:
                angle = math.pi / 2
            max_plate_postion_x = math.sin(angle)
            max_plate_postion_y = math.cos(angle)
        else:
            max_plate_postion_x = canvas_aspect_ratio if canvas_aspect_ratio > 1 else 1
            max_plate_postion_y = 1/canvas_aspect_ratio if canvas_aspect_ratio < 1 else 1

        assert (round(abs(point[0]),5) <= round(abs(max_plate_postion_x),5) and
                round(abs(point[1]),5) <= round(abs(max_plate_postion_y),5)
        )


@pytest.mark.usefixtures('setup_app', 'random_test_art_ids')
@pytest.mark.fill_canvas(True)
def test_all_points_scaled_correctly(art_dimensions):
    all_plate_positions, all_pixels, canvas, grid_size = art_dimensions
        
    for plate_position, pixel in zip(all_plate_positions, all_pixels):
        translated_pixel_x = pixel[1] - (grid_size[0] / 2)
        translated_pixel_y = -pixel[0] + (grid_size[1] / 2)

        if translated_pixel_x > 0 and translated_pixel_y > 0: #Can't draw conclusions about scaling if at 0 position
            assert round(plate_position[0] / translated_pixel_x, 5) == round(plate_position[1] / translated_pixel_y, 5)


@pytest.mark.usefixtures('setup_app', 'random_test_art_ids')
@pytest.mark.fill_canvas(True)
def test_full_plate_used(art_dimensions):
    all_plate_positions, all_pixels, canvas, grid_size = art_dimensions
    
    art_aspect_ratio = grid_size[0] / grid_size[1]
    
    if canvas.shape == 'round':
        angle = math.atan(art_aspect_ratio)
        max_art_position_x = math.sin(angle)
        max_art_position_y = math.cos(angle)
    else:
        canvas_aspect_ratio = canvas.x_radius_mm / canvas.y_radius_mm
        max_plate_position_x = canvas_aspect_ratio if canvas_aspect_ratio > 1 else 1
        max_plate_position_y = 1/canvas_aspect_ratio if canvas_aspect_ratio < 1 else 1
        wellspacing_x = max_plate_position_x * 2 / grid_size[0]
        wellspacing_y = max_plate_position_y * 2 / grid_size[1]
        wellspacing = min(wellspacing_x, wellspacing_y)
        max_art_position_x = wellspacing * grid_size[0] / 2
        max_art_position_y = wellspacing * grid_size[1] / 2
    
    max_reached_x, max_reached_y = (0, 0)
    for position in all_plate_positions:
        if position[0] > max_reached_x: max_reached_x = position[0]
        if position[1] > max_reached_y: max_reached_y = position[1]
        
    assert (round(max_reached_x, 5) == round(max_art_position_x, 5) and
            round(max_reached_y, 5) == round(max_art_position_y, 5)
    )