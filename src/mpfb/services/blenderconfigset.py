"""Functionality for storing configuration settings on blender entities"""

import os, json
from fnmatch import fnmatch
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, FloatProperty, FloatVectorProperty
from .logservice import LogService
from .configurationset import ConfigurationSet

_LOG = LogService.get_logger("configuration.blenderconfigset")

_PREFIX = "MPFB_"

class BlenderConfigSet(ConfigurationSet):
    """
    The BlenderConfigSet class is a concrete implementation of the abstract ConfigurationSet class, specifically designed
    to manage configuration settings within Blender. It extends the functionality provided by ConfigurationSet to handle
    Blender-specific properties and entities.

    The primary purpose of the BlenderConfigSet class is to provide a structured way to manage and interact with configuration
    settings within Blender. It allows for defining, retrieving, setting, and displaying properties on Blender entities, making
    it easier to handle complex configurations in a Blender environment.
    """

    def __init__(self, properties, bpy_type, prefix="", *, lowercase_prefix=False, getter_factory=None, setter_factory=None):
        _LOG.debug("Constructing new blender config set with prefix", prefix)
        self._properties_by_short_name = dict()
        self._properties_by_full_name = dict()
        self._prop_to_aliases = dict()
        self._alias_to_prop = dict()
        self._prefix = (_PREFIX.lower() if lowercase_prefix else _PREFIX) + prefix
        self._bpytype = bpy_type
        _LOG.debug("Full prefix is", self._prefix)

        self.getter_factory = None
        self.setter_factory = None

        if getter_factory is not None:
            self.getter_factory = getter_factory
        if setter_factory is not None:
            self.setter_factory = setter_factory

        for prop in properties:
            self.add_property(prop)

    def get_type(self):
        """Getter for the type of Blender entity this configuration set manages."""
        _LOG.enter()
        return self._bpytype

    def get_fullname_key_from_shortname_key(self, key_name):
        """
        Constructs the full property name using the prefix and the provided short name.

        Args:
            key_name (str): The short name of the property.

        Returns:
            str: The full property name with the prefix.
        """
        return self._prefix + key_name

    @staticmethod
    def get_definitions_in_json_directory(properties_dir):
        """
        Reads property definitions from JSON files in the specified directory.

        Args:
            properties_dir (str): The directory containing JSON files with property definitions.

        Returns:
            list: A list of property definitions read from the JSON files.

        Raises:
            IOError: If there is an error reading the properties from a JSON file.
        """
        _LOG.enter()
        _LOG.debug("Scanning properties dir", properties_dir)
        known_properties = []
        for file_name in os.listdir(properties_dir):
            _LOG.trace("file name", file_name)
            if fnmatch(file_name, "*.json"):
                json_file_name = os.path.join(properties_dir, file_name)
                _LOG.debug("Trying to add properties from file", json_file_name)
                try:
                    with open(json_file_name, encoding="utf-8") as json_file:
                        data = json.load(json_file)
                        _LOG.dump("Json from file", data)
                        known_properties.append(data)
                except Exception as e:
                    _LOG.error("FAILED to add properties from file", os.path.abspath(json_file_name))
                    _LOG.error("Exception was", e)
                    raise IOError("Failed to read properties from " + str(json_file))
        return known_properties

    def check_and_transform_entity_reference(self, entity_reference):
        """
        Validates and transforms the entity reference to ensure it matches the expected Blender type.

        Args:
            entity_reference: The entity reference to check and transform.

        Returns:
            The validated and transformed entity reference.

        Raises:
            ValueError: If the entity reference is None or not an instance of the expected Blender type.
        """
        _LOG.debug("Entity, entity type, bpy type", (entity_reference, type(entity_reference), self._bpytype))
        if entity_reference is None:
            raise ValueError('Must provide a valid entity reference in order to read a BlenderConfigSet value')
        if not isinstance(entity_reference, self._bpytype):
            raise ValueError('This entity reference is not an instance of ' + str(self._bpytype.__name__))
        return entity_reference

    def get_value(self, name, default_value=None, entity_reference=None):
        """
        Retrieves the value of a property from a Blender entity.

        Args:
            name (str): The name of the property.
            default_value (optional): The default value to return if the property is not found.
            entity_reference (optional): The Blender entity reference to retrieve the property value from.

        Returns:
            The value of the property, or the default value if the property is not found.
        """
        _LOG.enter()
        entity_reference = self.check_and_transform_entity_reference(entity_reference)
        prop = None
        if name in self._properties_by_short_name:
            prop = self._properties_by_short_name[name]
        if name in self._properties_by_full_name:
            prop = self._properties_by_full_name[name]
        if prop is None:
            if name in self._alias_to_prop:
                real_name = self._alias_to_prop[name]
                prop = self._properties_by_full_name[real_name]
        if prop is None:
            _LOG.warn("Tried to read value from non-existing key", name)
            return default_value
        full_name = prop["full_name"]

        _LOG.debug("property name", full_name)

        try:
            if not hasattr(entity_reference, full_name):
                _LOG.warn("Tried to read non existing key from entity:", (full_name, entity_reference))
                return default_value
        except Exception as e:
            _LOG.error("Tried to read invalid/unreadable property", (full_name, entity_reference, e))
            return default_value

        _LOG.trace("found value", getattr(entity_reference, full_name))

        # TODO: check if defined first. If not, check if any alias is defined
        return getattr(entity_reference, full_name)

    def set_value(self, name, value, entity_reference=None):
        """
        Sets the value of a property on a Blender entity.

        Args:
            name (str): The name of the property.
            value: The value to set for the property.
            entity_reference (optional): The Blender entity reference to set the property value on.

        Raises:
            ValueError: If the property does not exist on the entity.
        """
        _LOG.enter()
        entity_reference = self.check_and_transform_entity_reference(entity_reference)

        prop = None
        if name in self._properties_by_short_name:
            prop = self._properties_by_short_name[name]
        if name in self._properties_by_full_name:
            prop = self._properties_by_full_name[name]
        if prop is None:
            _LOG.error("Tried to write value to non-existing key", name)
            _LOG.error("Possible short name keys are", self._properties_by_short_name.keys())
            _LOG.error("Possible full name keys are", self._properties_by_full_name.keys())
            _LOG.error("Possible aliases are", self._alias_to_prop.keys())
            raise ValueError('This entity has no property matching ' + name)
        full_name = prop["full_name"]

        _LOG.dump("About to set property", (self._bpytype, entity_reference, full_name, value))
        setattr(entity_reference, full_name, value)

        if full_name in self._prop_to_aliases:
            for alias in self._prop_to_aliases[full_name]:
                _LOG.dump("About to set alias", (self._bpytype, entity_reference, alias, value))
                setattr(entity_reference, alias, value)

    def get_keys(self):
        """
        Retrieves all the short names of the properties in the configuration set.

        Returns:
            dict_keys: A view object that displays a list of all the short names of the properties.
        """
        _LOG.enter()
        return self._properties_by_short_name.keys()

    def has_key(self, name):
        """
        Checks if a property with the given name exists in the configuration set.

        Args:
            name (str): The name of the property to check.

        Returns:
            bool: True if the property exists, False otherwise.
        """
        _LOG.enter()
        return name in self._properties_by_full_name or name in self._properties_by_short_name or name in self._alias_to_prop

    def has_key_with_value(self, name, entity_reference=None):
        """
        Checks if a property with the given name exists and has a value in the configuration set.

        Args:
            name (str): The name of the property to check.
            entity_reference (optional): The Blender entity reference to check the property value on.

        Returns:
            bool: True if the property exists and has a value, False otherwise.
        """
        _LOG.enter()
        if not self.has_key(name):
            return False
        value = self.get_value(name, entity_reference=entity_reference)
        return not value is None

    def _create_property_by_type(self, proptype, name, description, default, items=None, items_callback=None, min=None, max=None):
        entity_property = None
        getter = None
        setter = None
        if self.getter_factory is not None:
            getter = self.getter_factory(self, name)
        if self.setter_factory is not None:
            setter = self.setter_factory(self, name)

        _LOG.debug("Getter, setter factories", (self.getter_factory, self.setter_factory))
        _LOG.debug("Getter, setter", (getter, setter))

        if proptype == "boolean":
            entity_property = BoolProperty(name=name, description=description, default=default, get=getter, set=setter)  # pylint: disable=E1111
        if proptype == "string":
            entity_property = StringProperty(name=name, description=description, default=default, get=getter, set=setter)  # pylint: disable=E1111

        if proptype == "path":
            entity_property = StringProperty(name=name, description=description, default=default,
                                         subtype='FILE_PATH', get=getter, set=setter)
        if proptype == "dir_path":
            entity_property = StringProperty(name=name, description=description, default=default,
                                         subtype='DIR_PATH', get=getter, set=setter)
        if proptype == "int":
            entity_property = IntProperty(name=name, description=description, default=default, get=getter, set=setter)  # pylint: disable=E1111
        if proptype == "float":
            if min is None:
                entity_property = FloatProperty(name=name, description=description, default=default, get=getter, set=setter)  # pylint: disable=E1111
            else:
                entity_property = FloatProperty(name=name, description=description, default=default, min=min, max=max, get=getter, set=setter)  # pylint: disable=E1111
        if proptype == "vector_location":
            entity_property = FloatVectorProperty(name=name, description=description, default=default,
                                                  size=3, subtype='XYZ', unit='LENGTH', get=getter, set=setter)
        if proptype == "color":
                entity_property = FloatVectorProperty(name=name, description=description, default=default,
                                                      size=4, subtype='COLOR', min=0.0, max=1.0, get=getter, set=setter)

        if proptype == "enum":
            enumitems = []
            if items:
                for item in items:
                    enumitems.append(tuple(item))
            if not items_callback is None:
                enumitems = items_callback
            entity_property = EnumProperty(# pylint: disable=E1111
                name=name,
                description=description,
                default=default,
                items=enumitems, get=getter, set=setter)

        return entity_property

    def add_property(self, prop, items_callback=None, override_prefix=None):
        """
        Adds a new property to the configuration set and defines it on the Blender entity type.

        Args:
            prop (dict): A dictionary containing the property definition. Expected keys include:
                - name (str): The short name of the property.
                - type (str): The type of the property (e.g., "boolean", "string", "int", "float", "vector_location", "enum", "color").
                - description (str): A description of the property.
                - default: The default value of the property.
                - aliases (list, optional): A list of alias names for the property.
                - min (optional): The minimum value for the property (if applicable).
                - max (optional): The maximum value for the property (if applicable).
                - items (list, optional): A list of items for enum properties.
            items_callback (callable, optional): A callback function to provide items for enum properties.

        Raises:
            ValueError: If the property type is not recognized.
        """
        _LOG.enter()
        copied_property = dict(prop)
        copied_property["full_name"] = self._prefix + copied_property["name"]
        if override_prefix:
            copied_property["full_name"] = override_prefix + copied_property["name"]
        self._properties_by_full_name[copied_property["full_name"]] = copied_property
        self._properties_by_short_name[copied_property["name"]] = copied_property
        _LOG.debug("Defining property", copied_property["full_name"])

        if "aliases" in prop:
            self._prop_to_aliases[copied_property["full_name"]] = prop["aliases"]
            for alias in prop["aliases"]:
                self._alias_to_prop[alias] = copied_property["full_name"]

        min = None
        max = None
        if "min" in copied_property:
            min = copied_property["min"]
        if "max" in copied_property:
            max = copied_property["max"]

        items = None
        if "items" in copied_property:
            items = copied_property["items"]
        entity_property = self._create_property_by_type(
            copied_property["type"],
            copied_property["full_name"],
            copied_property["description"],
            copied_property["default"],
            items,
            items_callback,
            min=min,
            max=max)

        _LOG.dump("Adding entity property:", (str(copied_property["full_name"]), entity_property))

        setattr(self._bpytype, str(copied_property["full_name"]).strip(), entity_property)

        if "aliases" in prop:
            self._prop_to_aliases[copied_property["full_name"]] = prop["aliases"]
            for alias in prop["aliases"]:
                self._alias_to_prop[alias] = copied_property["full_name"]
                alias_property = self._create_property_by_type(
                    copied_property["type"],
                    alias,
                    copied_property["description"],
                    copied_property["default"],
                    items,
                    items_callback)
                _LOG.dump("Adding alias property", (str(alias), alias_property))
                setattr(self._bpytype, str(alias).strip(), alias_property)

    def _find_property(self, name):
        prop = None
        if name in self._properties_by_short_name:
            prop = self._properties_by_short_name[name]
        if name in self._properties_by_full_name:
            prop = self._properties_by_full_name[name]
        return prop

    def draw_properties(self, entity_reference, component_to_draw_on, property_names, *, text=None, **kwargs):
        """
        Draws the specified properties on a Blender UI component.

        Args:
            entity_reference: The Blender entity reference to draw the properties from.
            component_to_draw_on: The Blender UI component (e.g., a box) to draw the properties on.
            property_names (list): A list of property names to draw.
            text (str, optional): The text label to use for the properties. If None, the property label is used.
            **kwargs: Additional keyword arguments to pass to the Blender UI component's prop method.

        Raises:
            ValueError: If the entity_reference or component_to_draw_on is None.
        """
        _LOG.enter()
        if entity_reference is None:
            raise ValueError('Must provide a valid blender entity reference in order to draw properties')
        if component_to_draw_on is None:
            raise ValueError('Must provide a valid blender UI component, such as a box, in order to draw properties')
        if property_names is None or len(property_names) < 1:
            return

        for name in property_names:
            prop = self._find_property(name)
            _LOG.debug("Drawing property", (name, type(prop), prop))
            if prop is None:
                _LOG.warn("Tried to draw a non-existing property", name)
                self.deferred_draw_property(entity_reference, component_to_draw_on, name, text)
            else:
                label = prop.get("label", "") if text is None else text
                is_default = True
                if "type" in prop and "subtype" in prop:
                    if prop["type"] == "boolean" and prop["subtype"] == "panel_toggle":
                        is_default = False
                        is_open = self.get_value(prop["name"], False, entity_reference=entity_reference)
                        icon = 'TRIA_DOWN' if is_open else 'TRIA_RIGHT'
                        component_to_draw_on.prop(entity_reference, prop["full_name"], text=label, icon=icon, emboss=True, **kwargs)
                if is_default:
                    component_to_draw_on.prop(entity_reference, prop["full_name"], text=label, **kwargs)

    def deferred_draw_property(self, entity_reference, component_to_draw_on, property_name, text=None):
        """Abstract method that can be overridden by subclasses to implement drawing logic for properties which
        are not known to the configset."""
        _LOG.debug("Deferred draw not overridden")


    def get_property_id_for_draw(self, name):
        """
        Retrieves the full property name for drawing purposes.

        Args:
            name (str): The short name of the property.

        Returns:
            str: The full property name if the property exists, None otherwise.
        """
        prop = self._find_property(name)

        if prop is None:
            _LOG.warn("Tried to draw a non-existing property", name)
            return None

        return prop["full_name"]
