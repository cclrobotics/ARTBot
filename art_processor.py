import json
import datetime.datetime

#Lists slots that should typically be available
def canvas_slot_generator():
    for slot in [1,2,4,5,7,8,9,10,11]:
        yield str(slot)
get_canvas_slot = slotter()


#Get JSON template
template_file = open('ART_TEMPLATE.json')
output_json = json.load(template_file)
template_file.close()

#Get list of dicts describing art
input_file = open('ART_INPUT.json')
input_json = json.load(input_file)
input_file.close()



#Make adjustments
output_json['metadata']['created'] = str(datetime.now())

for num, artpiece in enumerate(input_json):
	output_json['labware']['canvas%s' % num] = {
		'slot': next(get_canvas_slot)
		,'display-name': 'Canvas %s' % num
		,'model': 'CCL_canvas'
	}

#For each job, make one step in "procedures" for each color used
# and one sub-step for each well to dispense to.
# (Might be some tricky math to manage distributing large amounts)
# Then each job just gets concatenated onto the end, so it's one big list

#Can this JSON-schema handle notifications (or tweets????)