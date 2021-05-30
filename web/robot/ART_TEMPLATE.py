from opentrons import protocol_api
from opentrons.types import Location
import math

metadata = {
    'apiLevel': '2.8',
    'protocolName': 'CCL ARTBot',
    'author': 'Tim Dobbs and Counter Culture Labs',
    'source': 'ARTBot Protocol Builder',
    'description': """Protocol for drawing bio-art.
                      Built from a template and the designer
                      at bioartbot.org"""
    }


def trace_diamond(pipette, point, vol, radius_pct = 2.4):
    corner_offsets = [(-radius_pct, 0, 0), (0, -radius_pct, 0), (radius_pct, 0, 0), (0, radius_pct, 0)]
    
    #close the loop so it makes a full diamond
    corner_offsets.append(corner_offsets[0])
    
    for num, corner_offset in enumerate(corner_offsets):
        corner = point.move(Point(*corner_offset))
        pipette.move_to(corner, force_direct = (num!=0))
        pipette.dispense(vol/4)

def bold_line(pipette, point, prev_point, vol, start_stroke = False):
    #Moves directly to the next point instead of following an arc
    #Then writes over itself to reinforce
    pipette.move_to(point, force_direct=not start_stroke)
    pipette.dispense(vol)
    pipette.move_to(prev_point, force_direct=True)
    pipette.move_to(point, force_direct=True)

def penstroke(pipette, point, vol, stroke_length_max = 6, stroke_angle_max = 0.3490659):
    pipette.move_to(point, force_direct=False)
    pipette.dispense(vol)

    stroke_length = random.random() * stroke_length_max
    stroke_angle = random.random() * stroke_angle_max

    x_offset = stroke_length * math.cos(stroke_angle)
    y_offset = stroke_length * -math.cos(stroke_angle)

    endpoint = point.move(Point(x_offset, y_offset, 0.1))
    pipette.move_to(endpoint, force_direct=True)

    

def is_next_to(p1, p2, neighbor_dist = 3.4):
    p1 = p1.point
    p2 = p2.point

    dist = math.sqrt((p1[0] - p2[0])**2 +(p1[1] - p2[1])**2)

    return dist <= neighbor_dist



def distribute_to_agar(pipette, vol, source, destination, disposal_vol, shape=None):
    max_volume = pipette.max_volume

    dest = list(destination)  # allows for non-lists

    prev_well = None
    for cnt, well in enumerate(dest):
        full_pipette = False
        if (cnt + 1) % 150 == 0:
            pipette.drop_tip()

        if not pipette.has_tip:
            pipette.pick_up_tip()

        if pipette.current_volume < (vol + disposal_vol):
            remaining_wells = len(dest) - cnt
            remaining_vol = remaining_wells * vol

            if remaining_vol + disposal_vol > max_volume:
                asp_vol = math.floor((max_volume - disposal_vol) / vol) * vol + disposal_vol - pipette.current_volume
            else:
                asp_vol = remaining_vol + disposal_vol - pipette.current_volume

            pipette.aspirate(asp_vol, source)
            full_pipette = True
        
        if shape is None: shape = ''
        if shape == 'diamond':
            trace_diamond(pipette, well, vol)
        elif shape == 'line' and prev_well and is_next_to(well, prev_well):
            bold_line(pipette, well, prev_well, vol, start_stroke=full_pipette)
        elif shape == 'penstroke':
            penstroke(pipette, well, vol)
        else:
            pipette.move_to(well)
            pipette.dispense(vol)

        prev_well = well

    pipette.drop_tip()


def run(protocol: protocol_api.ProtocolContext):  
    # a tip rack for our pipette
    tiprack = protocol.load_labware('%%TIPRACK GOES HERE%%', 10)

    # a plate for all of the colors in our pallette
    palette = protocol.load_labware('%%PALETTE GOES HERE%%', 11)

    # set the pipette we will be using
    pipette = protocol.load_instrument(
            '%%PIPETTE GOES HERE%%',
            mount='left',
            tip_racks=[tiprack]
    )

    # load all of the 
    pixels_by_color_by_artpiece = %%PIXELS GO HERE%%
    canvas_locations = %%CANVAS LOCATIONS GO HERE%%
    color_map = %%COLORS GO HERE%%

    # a function that gets us the next available well in a plate
    def well_generator(plate):
        for well in plate.wells():
            yield well
    get_well = well_generator(palette)

    # colored culture locations
    palette_colors = { color: next(get_well) for color in pixels_by_color_by_artpiece.keys() }
    protocol.comment('**CHECK BEFORE RUNNING** - Colors should be loaded into these wells:')
    for color in palette_colors:
        protocol.comment(f'{color_map[color]} -> {palette_colors[color]}')

    # plates to create art in
    canvas_labware = dict()
    for art_title in canvas_locations:
        canvas_labware[art_title] = protocol.load_labware('ccl_artbot_canvas', canvas_locations[art_title])

    # wells to dispense each color material to
    pixels_by_color = dict()
    for color in pixels_by_color_by_artpiece:
        pixels_by_color[color] = list()
        pixels_by_artpiece = pixels_by_color_by_artpiece[color]
        for art_title in pixels_by_artpiece:
            pixels_by_color[color] += [
                Location(
                    point=canvas_labware[art_title].wells()[0].from_center_cartesian(x=pixel[0], y=pixel[1], z=-0.5),
                    labware=canvas_labware[art_title]
                 )
                for pixel in pixels_by_artpiece[art_title]
            ]
            if not len(pixels_by_artpiece[art_title]): #single-well case
                pixel = pixels_by_artpiece[art_title]
                pixels_by_color[color] += [
                    Location(
                        point=canvas_labware[art_title].wells()[0].from_center_cartesian(x=pixel[0], y=pixel[1], z=-0.5),
                        labware=canvas_labware[art_title]
                    )
                ]

    #This is a quick check that the pipette is calibrated to pick up tip at the bottom row as well as the top
    pipette.pick_up_tip(tiprack.wells()[7])
    pipette.return_tip()

    for color in pixels_by_color:
        distribute_to_agar(pipette, 0.1, palette_colors[color], pixels_by_color[color], disposal_vol=1)