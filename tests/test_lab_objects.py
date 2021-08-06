import pytest
from web.api.lab_objects.lab_objects import LabObject, LabObjectPropertyCollection
from .conftest import VALID_PLATE

VALID_PLATE = VALID_PLATE['ccl_artbot_canvas_90mm_round']
VALID_PLATE_NAME = VALID_PLATE[0]
VALID_PLATE_CLASS = VALID_PLATE[1]
VALID_PROPERTIES = VALID_PLATE[2]


def validate_properties(properties_as_dict, obj):
    for prop in properties_as_dict:
        units = f'_{prop.get("units")}' if prop.get('units') else ''
        name_in_obj = prop['name'] + units
        val_in_obj = getattr(obj, name_in_obj)
        assert val_in_obj == prop['value']
        assert obj.properties[name_in_obj].value == prop['value']
        if prop.get('units'):
            assert obj.properties[name_in_obj].units == prop['units']
        assert obj.properties[name_in_obj]._db_name == prop['name']
        assert obj.properties[name_in_obj]._name == name_in_obj
    return True


def test_lab_object_create():
    properties = VALID_PROPERTIES
    property_collection = LabObjectPropertyCollection.from_dicts(properties)
    obj = LabObject(VALID_PLATE_NAME, VALID_PLATE_CLASS, property_collection)
    assert obj.name == VALID_PLATE_NAME and obj.object_class == VALID_PLATE_CLASS
    assert validate_properties(properties, obj)

@pytest.mark.usefixtures('setup_app')
def test_lab_object_create_in_db():
    properties = VALID_PROPERTIES
    property_collection = LabObjectPropertyCollection.from_dicts(properties)
    LabObject._create_in_db(VALID_PLATE_NAME, VALID_PLATE_CLASS, property_collection)
    
    obj = LabObject.load_from_name(VALID_PLATE_NAME)
    assert obj.name == VALID_PLATE_NAME and obj.object_class == VALID_PLATE_CLASS
    assert validate_properties(properties, obj)

def test_lab_object_unknown_property():
    properties = VALID_PROPERTIES
    property_collection = LabObjectPropertyCollection.from_dicts(properties)
    obj = LabObject(VALID_PLATE_NAME, VALID_PLATE_CLASS, property_collection)
    with pytest.raises(AttributeError):
        obj.INVALID_ATTRIBUTE_NAME
    obj.INVALID_ATTRIBUTE_NAME = 5
    assert obj.INVALID_ATTRIBUTE_NAME == 5

def test_lab_object_property_update():
    properties = VALID_PROPERTIES
    property_collection = LabObjectPropertyCollection.from_dicts(properties)
    obj = LabObject(VALID_PLATE_NAME, VALID_PLATE_CLASS, property_collection)

    assert obj.x_radius_mm == 40
    obj.x_radius_mm = 80

    assert obj.x_radius_mm == 80
    assert obj.properties['x_radius_mm'].value == 80

@pytest.mark.usefixtures('setup_app')
def test_lab_object_model_update():
    properties = VALID_PROPERTIES
    property_collection = LabObjectPropertyCollection.from_dicts(properties)
    LabObject._create_in_db(VALID_PLATE_NAME, VALID_PLATE_CLASS, property_collection)
    
    obj = LabObject.load_from_name(VALID_PLATE_NAME)
    obj.name = 'NEW_VALID_NAME'
    obj.object_class = 'NEW_VALID_OBJECT_CLASS'
    obj.x_radius_mm = 90
    obj.shape = 'rectangle'

    obj.save()

    new_obj = LabObject.load_from_name('NEW_VALID_NAME')
    assert new_obj.name == 'NEW_VALID_NAME'
    assert new_obj.object_class == 'NEW_VALID_OBJECT_CLASS'
    assert new_obj.x_radius_mm == 90
    assert new_obj.properties['x_radius_mm'].value == 90
    assert new_obj.shape == 'rectangle'
    assert new_obj.properties['shape'].value == 'rectangle'