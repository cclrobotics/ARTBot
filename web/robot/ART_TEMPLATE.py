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


def distribute_to_agar(pipette, vol, source, destination, disposal_vol):
    max_volume = pipette.max_volume
    needs_new_tip = True

    dest = list(destination)  # allows for non-lists

    for cnt, well in enumerate(dest):
        if (cnt + 1) % 150 == 0:
            needs_new_tip = True

        if not pipette.has_tip:
            pipette.pick_up_tip()

        if pipette.current_volume < (vol + disposal_vol):
            if needs_new_tip:
                if pipette.has_tip: pipette.drop_tip()
                pipette.pick_up_tip()
                needs_new_tip = False
                
            remaining_wells = len(dest) - cnt
            remaining_vol = remaining_wells * vol

            if remaining_vol + disposal_vol > max_volume:
                asp_vol = math.floor((max_volume - disposal_vol) / vol) * vol + disposal_vol - pipette.current_volume
            else:
                asp_vol = remaining_vol + disposal_vol - pipette.current_volume

            pipette.aspirate(asp_vol, source)

        pipette.move_to(well)
        pipette.dispense(vol)


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
        canvas_labware[art_title] = protocol.load_labware('%%CANVAS GOES HERE%%', canvas_locations[art_title])

    # wells to dispense each color material to
    pixels_by_color = dict()
    for color in pixels_by_color_by_artpiece:
        pixels_by_color[color] = list()
        pixels_by_artpiece = pixels_by_color_by_artpiece[color]
        for art_title in pixels_by_artpiece:
            pixels_by_color[color] += [
                Location(
                    point=canvas_labware[art_title].wells()[0].from_center_cartesian(x=pixel[0], y=pixel[1], z=pixel[2]),
                    labware=canvas_labware[art_title]
                 )
                for pixel in pixels_by_artpiece[art_title]
            ]
            if not len(pixels_by_artpiece[art_title]): #single-well case
                pixel = pixels_by_artpiece[art_title]
                pixels_by_color[color] += [
                    Location(
                        point=canvas_labware[art_title].wells()[0].from_center_cartesian(x=pixel[0], y=pixel[1], z=pixel[2]),
                        labware=canvas_labware[art_title]
                    )
                ]

    for color in pixels_by_color:
        distribute_to_agar(pipette, 0.4, palette_colors[color], pixels_by_color[color], disposal_vol=2)
