import re

from web.database.models import LabObjectsModel, LabObjectPropertyModel

_Model = LabObjectsModel
_ParamModel = LabObjectPropertyModel

class LabObject():
    def __init__(self, name):
        self._model = _Model.query.filter(_Model.name == name).one_or_none()
        self._properties = self._model.properties.all()

        #Expect few properties. If this changes, don't do this by iteration
        for prop in self._properties:
            units = f'_{prop.obj_property_units}' if prop.obj_property_units else ''
            setattr(self,
                    prop.obj_property + units,
                    prop.property_value_num or prop.property_value_str
            )
        self.object_class = self._model.obj_class
        self.name = self._model.name
    
    @classmethod
    def _create(cls, name, obj_class, property_list: list):
        properties = [_ParamModel(**prop) for prop in property_list]
        _Model(name=name, obj_class=obj_class, properties=properties).save()
        return cls(name)
        
    
    @classmethod
    def object_types(obj_class: str=None):
        """List all object types currently available
           obj_class is an optional filter to only show types
           of a certain class, e.g. "wellplates"
        """
        pass

    @classmethod
    def properties(object_type: str=None, filter: str=None):
        """List all properties stored in the database
           object_type shows only properties for an object type
           filter uses regexp to show properties that look like the string
        """
        pass