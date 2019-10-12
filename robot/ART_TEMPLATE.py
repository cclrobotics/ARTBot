from opentrons import labware, instruments, robot

metadata = {
    'protocolName': 'CCL ARTBot',
    'author': 'Tim Dobbs and Counter Culture Labs',
    'source': 'ARTBot Protocol Builder'
    }

example_csv = """
    blue, plate1-A1, plate1-C3, plate2-A1
    pink, plate1-A2, plate2-B1, plate2-B2
"""

def run_custom_protocol(
    pixel_file: FileInput = example_csv,
)
    def distribute_to_agar(self, vol, source, destination, disposal_vol):

        dest = list(destination) #allows for non-lists

        for cnt, well in enumerate(dest):
            if not self.current_tip():
                self.pick_up_tip()

            if self.current_volume < (vol + disposal_vol):
                remaining_wells = len(dest) - cnt
                remaining_vol = remaining_wells * vol

                if remaining_vol + disposal_vol > self.max_volume:
                    asp_vol = math.floor((self.max_volume - disposal_vol) / vol) * vol
                else:
                    asp_vol =  remaining_vol + disposal_vol

                self.aspirate(asp_vol, source)

            self.dispense(vol, well, 0.25)

            dip_position = robot._driver.position
            dip_position['Z'] = dip_position['Z'] - 12 #tweek number to just pierce agar surface
            robot._driver.move(dip_position)

        self.drop_tip()

    # a 6-well plate for all of the colors in our pallette
    palette = labware.load('falcon_6_wellplate_15.5ml_flat', 11)

    # a tip rack for our pipette
    p200rack = labware.load('tiprack-200ul', 10)

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
        for line in pixels:
            color = line[0]

            color_list = line[:1]
            color_dict = dict()
            for plate_loc in color_list:
                 plate, location = plate_loc.split('-')
                color_dict[plate] = location

            pixel_dict[color] = color_dict


    pixels_by_color_by_artpiece = parse_pixels(pixel_file)
    canvas_locations = {'plate1':1,'plate2':2}

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
            pixels_by_color[color] += [
                pixel.top() for pixel in canvas_labware[art_title].wells(pixels_by_artpiece[art_title])
            ]


    def run(
            pipette_axis: 'StringSelection...'='left'):

        p300 = instruments.P300_Single(
                mount=pipette_axis,
                tip_racks=[p200rack]
        )

        for color in pixels_by_color:
            distribute_to_agar(p300, 0.1, palette_colors[color], pixels_by_color[color], disposal_vol=1)

