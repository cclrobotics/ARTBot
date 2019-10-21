from opentrons import labware
from opentrons.data_storage import database

#Set to True to replace labware definition if it already exists in robot
#If false, ignores any labware that is already defined in robot
REPLACE = False

#define a dict of custom plates. Can add as many as necessary
custom_plates = dict()

custom_plates['CCL_ARTBot_canvas'] = dict(
	grid=(39, 36),
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

custom_plates['nunc_8_wellplate_flat'] = dict(
	grid=(4, 2),
	spacing=(31, 40.5),
	diameter=31,
	depth=13.3,
	volume=13000
)

for plate_name in custom_plates:
	if plate_name in labware.list():
		if REPLACE:
			database.delete_container(plate_name)
		else:
			continue
	labware.create(plate_name, **custom_plates[plate_name])