from opentrons import labware, instruments, robot
import math

metadata = {
    'protocolName': 'CCL ARTBot',
    'author': 'Tim Dobbs and Counter Culture Labs',
    'source': 'ARTBot Protocol Builder'
    }


def distribute_to_agar(self, vol, source, destination, disposal_vol):
    self.max_volume = 20

    dest = list(destination)  # allows for non-lists

    for cnt, well in enumerate(dest):
        if (cnt + 1) % 150 == 0:
            self.drop_tip()
            self.current_volume = 0

        if not self.current_tip():
            self.pick_up_tip()

        if self.current_volume < (vol + disposal_vol):
            remaining_wells = len(dest) - cnt
            remaining_vol = remaining_wells * vol

            if remaining_vol + disposal_vol > self.max_volume:
                asp_vol = math.floor((self.max_volume - disposal_vol) / vol) * vol + disposal_vol - self.current_volume
            else:
                asp_vol = remaining_vol + disposal_vol - self.current_volume

            self.aspirate(asp_vol, source)

        self.dispense(vol, well, 0.25)

        dip_position = robot._driver.position
        dip_position['Z'] = dip_position['Z'] - 11
        robot._driver.move(dip_position)

    self.drop_tip()

# a tip rack for our pipette
p200rack = labware.load('tiprack-200ul', 10)

pixels_by_color_by_artpiece = %%PIXELS GO HERE%%
canvas_locations = %%CANVAS LOCATIONS GO HERE%%
wellplate_type = %%WELLPLATE TYPE GO HERE%%

# a well plate for all of the colors in our pallette
palette = labware.load(wellplate_type, 11)

# colored culture locations
palette_colors = dict(
    pink = palette.wells('A1')
    ,blue = palette.wells('A2')
    ,teal = palette.wells('A3')
    ,orange = palette.wells('B1')
    ,yellow = palette.wells('B2')
    )

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


def run_custom_protocol():

    p300 = instruments.P300_Single(
            mount='left',
            tip_racks=[p200rack]
    )

    for color in pixels_by_color:
        distribute_to_agar(p300, 0.1, palette_colors[color], pixels_by_color[color], disposal_vol=4)

run_custom_protocol()

