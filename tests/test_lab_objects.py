import pytest
from web.api.lab_objects.lab_objects import LabObject

@pytest.mark.usefixtures('test_app', 'test_database')
def test_lab_object_create():
    properties = [
        {'obj_property': 'x_dim', 'obj_property_units': 'mm', 'property_value_num':45},
        {'obj_property': 'y_dim', 'obj_property_units': 'mm', 'property_value_num':45},
        {'obj_property': 'z_touch_position', 'obj_property_units': 'frac', 'property_value_num':0.5},
        {'obj_property': 'shape', 'property_value_str':'square'},
    ]
    obj = LabObject._create('90mm_plate','labware',properties)
    assert obj.name == '90mm_plate' and obj.object_class == 'labware'
    for prop in properties:
        units = f'_{prop.get("obj_property_units")}' if prop.get('obj_property_units') else ''
        val_in_obj = getattr(obj, prop['obj_property'] + units)
        assert val_in_obj == prop.get('property_value_num') or val_in_obj == prop.get('property_value_str')