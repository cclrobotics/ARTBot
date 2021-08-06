from collections import namedtuple
from numbers import Number
import re
from web.api.lab_objects.serializers import LabObjectPropertySchema
from web.database.models import LabObjectsModel, LabObjectPropertyModel
from .serializers import LabObjectPropertySchema

_Model = LabObjectsModel
_ParamModel = LabObjectPropertyModel

class LabObjectProperty():
    def __init__(self, name, value, units=None):
        self.value = value
        if units: self.units = units
        self._name = "_".join([name,units]) if units else name
        self._db_name = name

    @classmethod
    def _from_model(cls, props_as_model):
        name = props_as_model.obj_property
        value = props_as_model.property_value_num or props_as_model.property_value_str
        units = props_as_model.obj_property_units
        return cls(name, value, units)

    @classmethod
    def from_dict(cls, prop_as_dict):
        schema = LabObjectPropertySchema()
        prop = schema.load(prop_as_dict)
        return cls(**prop)

    def _as_model(self):
        model = _ParamModel(obj_property = self._db_name)
        if hasattr(self, 'units'): model.obj_property_units = self.units
        if isinstance(self.value, Number):
            model.property_value_num = self.value
        else:
            model.property_value_str = self.value
        return model

    def as_dict(self):
        schema = LabObjectPropertySchema()
        return schema.dump(self)

    def __repr__(self):
        return f'<LabObjectProperty: {self._name} = {self.value}>'




class LabObjectPropertyCollection(dict):
    @classmethod
    def _from_model(cls, props_as_model):
        props_as_props = [LabObjectProperty._from_model(prop) for prop in props_as_model]
        collection = {prop._name:prop for prop in props_as_props}
        return cls(collection)

    @classmethod
    def from_dicts(cls, prop_list):
        props_as_props = [LabObjectProperty.from_dict(prop) for prop in prop_list]
        collection = {prop._name:prop for prop in props_as_props}
        return cls(collection)

    def as_model(self):
        return [prop._as_model() for prop in self.values()]

    def as_json(self):
        return LabObjectPropertySchema.dump(self.values(), many=True)
            
    def list(self):
        return self.keys()




class LabObject():
    def __init__(self, name: str, object_class: str, properties: LabObjectPropertyCollection, model: LabObjectsModel = None):
        self._model = model

        self.object_class = object_class
        self.name = name
        self.properties = properties
    
    #expose properties object as regular attributes
    def __getattr__(self, property):
        try:
            return self.properties[property].value
        except:
            raise AttributeError

    #allow updating of properties object as regular attributes
    def __setattr__(self, property, value):
        try:
            self.properties[property].value = value
        except (AttributeError, KeyError):
            self.__dict__[property] = value

    @classmethod
    def _create_in_db(cls, name, obj_class, properties: LabObjectPropertyCollection):
        if cls.load_from_name(name): return False
        model = _Model(name=name, obj_class=obj_class, properties=properties.as_model()).save()
        return model

    @classmethod
    def create_new(cls, name, obj_class, properties: list):
        property_collection = LabObjectPropertyCollection.from_dicts(properties)
        return cls(name, obj_class, property_collection)

    @classmethod
    def load_from_name(cls, name):
        try:
            _model = _Model.query.filter(_Model.name == name).one_or_none()
            _property_model = _model.properties.all()
        except AttributeError:
            return None

        properties = LabObjectPropertyCollection._from_model(_property_model)
        object_class = _model.obj_class
        name = _model.name
        return cls(name, object_class, properties, _model)
    
    @classmethod
    def stored_object_types(obj_class: str=None):
        """List all object types currently available
           obj_class is an optional filter to only show types
           of a certain class, e.g. "wellplates"
        """
        pass #TODO

    @classmethod
    def stored_properties(object_type: str=None, filter: str=None):
        """List all properties stored in the database
           object_type shows only properties for an object type
           filter uses regexp to show properties that look like the string
        """
        pass #TODO

    def save(self):
        if not self._model:
            self._model = self._create_in_db(self.name,
                                             self.object_class,
                                             self.properties
                                             )
            return
        self._model.name = self.name
        self._model.obj_class = self.object_class
        self._model.properties = self.properties.as_model()
        
        self._model.save()

    def __repr__(self):
        return f'<LabObject: {self.name}>'