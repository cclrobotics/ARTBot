from opentrons import labware, instruments, robot
from opentrons.data_storage import database
import math
import csv

class FileInput(object):
    def get_json(self):
        return {
            'type': 'FileInput'
        }

#Set to True to replace labware definition if it already exists in robot
#If false, ignores any labware that is already defined in robot
REPLACE = False

#define a dict of custom plates. Can add as many as necessary
custom_plates = dict()

custom_plates['CCL_ARTBot_canvas'] = dict(
	grid=(39, 26),
	spacing=(2.096, 2.096),
	diameter=0.75,
	depth=13,
	volume=7.5
)

custom_plates['falcon_6_wellplate_15.5ml_flat'] = dict(
	grid=(3, 2),
	spacing=(39.3, 39.3),
	diameter=34.75,
	depth=18,
	volume=15500
)

for plate_name in custom_plates:
	if plate_name in labware.list():
		if REPLACE:
			database.delete_container(plate_name)
		else:
			continue
	labware.create(plate_name, **custom_plates[plate_name])        


metadata = {
    'protocolName': 'CCL ARTBot',
    'author': 'Tim Dobbs and Counter Culture Labs',
    'source': 'ARTBot Protocol Builder'
    }

example_csv = """blue, plate1-A1, plate1-C3, plate2-A1
pink, plate1-A2, plate2-B1, plate2-B2"""

p200rack = labware.load('tiprack-200ul', 10)

p300 = instruments.P300_Single(
        mount='left',
        tip_racks=[p200rack]
)


def run_custom_protocol(pixel_file: FileInput = example_csv):
    def distribute_to_agar(vol, source, destination, disposal_vol):

        dest = list(destination) #allows for non-lists

        for cnt, well in enumerate(dest):
            p300.pick_up_tip()

            if p300.current_volume < (vol + disposal_vol):
                remaining_wells = len(dest) - cnt
                remaining_vol = remaining_wells * vol

                if remaining_vol + disposal_vol > p300.max_volume:
                    asp_vol = math.floor((p300.max_volume - disposal_vol) / vol) * vol
                else:
                    asp_vol =  remaining_vol + disposal_vol

                p300.aspirate(asp_vol, source)

            p300.dispense(vol, well, 0.25)

            dip_position = robot._driver.position
            dip_position['Z'] = dip_position['Z'] - 12 #tweek number to just pierce agar surface
            robot._driver.move(dip_position)

    # a 6-well plate for all of the colors in our pallette
    palette = labware.load('falcon_6_wellplate_15.5ml_flat', 11)

    # a tip rack for our pipett

    # colored culture locations
    palette_colors = dict(
        pink = palette.wells('A1')
        ,blue = palette.wells('A2')
        ,teal = palette.wells('A3')
        ,orange = palette.wells('B1')
        ,yellow = palette.wells('B2')
        )

    def parse_pixels(pixels):
        pixel_dict = dict()

        for row in pixels.splitlines():
            line = row.split(',')
            color = line[0]

            color_list = line[1:]
            color_dict = dict()
            for plate_loc in color_list:
                 plate, location = plate_loc.split('-')
                 color_dict[plate.strip()] = [location.strip()]

            pixel_dict[color] = color_dict
        return pixel_dict

    pixels_by_color_by_artpiece = parse_pixels(pixel_file)
    canvas_locations = {'plate1':'1','plate2':'2'}

    # plates to create art in
    canvas_labware = dict()
    for art_title in canvas_locations:
        canvas_labware[art_title] = labware.load('CCL_ARTBot_canvas', canvas_locations[art_title])

    # wells to dispense each color material to
    pixels_by_color = dict()
    for color in pixels_by_color_by_artpiece:
        pixels_by_color[color] = list()
        pixels_by_artpiece = pixels_by_color_by_artpiece[color]
        for art_title in pixels_by_artpiece:
            pixels_by_color[color] += [canvas_labware[art_title].wells(pixels_by_artpiece[art_title]).top()]

    for color in pixels_by_color:
        distribute_to_agar(0.1, palette_colors[color], pixels_by_color[color], disposal_vol=1)
        p300.drop_tip()

run_custom_protocol(**{'pixel_file': example_csv})