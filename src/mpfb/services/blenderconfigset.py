"""Functionality for storing configuration settings on blender entities"""

import os, json
from collections.abc import Callable, Collection, KeysView
from fnmatch import fnmatch
from typing import Any
import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, FloatProperty, FloatVectorProperty
from .logservice import LogService
from .configurationset import ConfigurationSet
from ..types import PropertyAccessorFactory, PropertyDefinition

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

    def __init__(self, properties: list[PropertyDefinition], bpy_type: type[bpy.types.bpy_struct], prefix: str = "", *,
                 lowercase_prefix: bool = False, getter_factory: PropertyAccessorFactory | None = None,
                 setter_factory: PropertyAccessorFactory | None = None) -> None:
        _LOG.debug("Constructing new blender config set with prefix", prefix)
        self._properties_by_short_name: dict[str, PropertyDefinition] = dict()
        self._properties_by_full_name: dict[str, PropertyDefinition] = dict()
        self._prop_to_aliases: dict[str, list[str]] = dict()
        self._alias_to_prop: dict[str, str] = dict()
        self._prefix: str = (_PREFIX.lower() if lowercase_prefix else _PREFIX) + prefix
        self._bpytype: type[bpy.types.bpy_struct] = bpy_type
        _LOG.debug("Full prefix is", self._prefix)

        self.getter_factory: PropertyAccessorFactory | None = None
        self.setter_factory: PropertyAccessorFactory | None = None

        if getter_factory is not None:
            self.getter_factory = getter_factory
        if setter_factory is not None:
            self.setter_factory = setter_factory

        for prop in properties:
            self.add_property(prop)

    def get_type(self) -> type[bpy.types.bpy_struct]:
        """Getter for the type of Blender entity this configuration set manages."""
        _LOG.enter()
        return self._bpytype

    def get_fullname_key_from_shortname_key(self, key_name: str) -> str:
        """
        Constructs the full property name using the prefix and the provided short name.

        Args:
            key_name (str): The short name of the property.

        Returns:
            str: The full property name with the prefix.
        """
        return self._prefix + key_name

    @staticmethod
    def get_definitions_in_json_directory(properties_dir: str) -> list[PropertyDefinition]:
        """
        Reads property definitions from JSON files in the specified directory.

        Args:
            properties_dir (str): The directory containing JSON files with property definitions.

        Returns:
            list[PropertyDefinition]: The property definitions read from the JSON files.

        Raises:
            IOError: If there is an error reading the properties from a JSON file.
        """
        _LOG.enter()
        _LOG.debug("Scanning properties dir", properties_dir)
        known_properties: list[PropertyDefinition] = []
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

    def check_and_transform_entity_reference(self, entity_reference: Any) -> Any:
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

    def get_value(self, name: str, default_value: Any = None, entity_reference: Any = None) -> Any:
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

    def set_value(self, name: str, value: Any, entity_reference: Any = None) -> None:
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

    def get_keys(self) -> KeysView[str]:
        """
        Retrieves all the short names of the properties in the configuration set.

        Returns:
            KeysView[str]: A view object that displays a list of all the short names of the properties.
        """
        _LOG.enter()
        return self._properties_by_short_name.keys()

    def has_key(self, name: str) -> bool:
        """
        Checks if a property with the given name exists in the configuration set.

        Args:
            name (str): The name of the property to check.

        Returns:
            bool: True if the property exists, False otherwise.
        """
        _LOG.enter()
        return name in self._properties_by_full_name or name in self._properties_by_short_name or name in self._alias_to_prop

    def has_key_with_value(self, name: str, entity_reference: Any = None) -> bool:
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

    def _create_property_by_type(self, proptype: str, name: str, description: str, default: Any, items: list[Any] | None = None,
                                 items_callback: Any = None, min: float | None = None, max: float | None = None,
                                 update_callback: Callable[[Any, bpy.types.Context], None] | None = None) -> Any:
        entity_property: Any = None
        getter: Any = None
        setter: Any = None
        if self.getter_factory is not None:
            getter = self.getter_factory(self, name)
        if self.setter_factory is not None:
            setter = self.setter_factory(self, name)

        _LOG.debug("Getter, setter factories", (self.getter_factory, self.setter_factory))
        _LOG.debug("Getter, setter", (getter, setter))

        # Blender refuses an explicit update= when get/set are also provided. Only forward the
        # update callback when no custom getter/setter is registered, which is the common case for
        # statically-defined properties.
        use_update = update_callback if (getter is None and setter is None) else None

        if proptype == "boolean":
            entity_property = BoolProperty(name=name, description=description, default=default, get=getter, set=setter, update=use_update)  # pylint: disable=E1111
        if proptype == "string":
            entity_property = StringProperty(name=name, description=description, default=default, get=getter, set=setter, update=use_update)  # pylint: disable=E1111

        if proptype == "path":
            entity_property = StringProperty(name=name, description=description, default=default,
                                         subtype='FILE_PATH', get=getter, set=setter, update=use_update)
        if proptype == "dir_path":
            entity_property = StringProperty(name=name, description=description, default=default,
                                         subtype='DIR_PATH', get=getter, set=setter, update=use_update)
        if proptype == "int":
            entity_property = IntProperty(name=name, description=description, default=default, get=getter, set=setter, update=use_update)  # pylint: disable=E1111
        if proptype == "float":
            if min is None:
                entity_property = FloatProperty(name=name, description=description, default=default, get=getter, set=setter, update=use_update)  # pylint: disable=E1111
            else:
                entity_property = FloatProperty(name=name, description=description, default=default, min=min, max=max, get=getter, set=setter, update=use_update)  # pylint: disable=E1111
        if proptype == "vector_location":
            entity_property = FloatVectorProperty(name=name, description=description, default=default,
                                                  size=3, subtype='XYZ', unit='LENGTH', get=getter, set=setter, update=use_update)
        if proptype == "color":
                entity_property = FloatVectorProperty(name=name, description=description, default=default,
                                                      size=4, subtype='COLOR', min=0.0, max=1.0, get=getter, set=setter, update=use_update)

        if proptype == "enum":
            enumitems: Any = []
            if items:
                for item in items:
                    enumitems.append(tuple(item))
            if not items_callback is None:
                enumitems = items_callback
            entity_property = EnumProperty(# pylint: disable=E1111
                name=name,
                description=description,
                default=default,
                items=enumitems, get=getter, set=setter, update=use_update)

        return entity_property

    def add_property(self, prop: PropertyDefinition, items_callback: Any = None, override_prefix: str | None = None,
                     update_callback: Callable[[Any, bpy.types.Context], None] | None = None) -> None:
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
            update_callback (callable, optional): An update callback for the bpy property; called when
                the value changes in the UI. Signature: ``fn(self, context)``.

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

        min: float | None = None
        max: float | None = None
        if "min" in copied_property:
            min = copied_property["min"]
        if "max" in copied_property:
            max = copied_property["max"]

        items: list[Any] | None = None
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
            max=max,
            update_callback=update_callback)

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

    def _find_property(self, name: str) -> PropertyDefinition | None:
        prop: PropertyDefinition | None = None
        if name in self._properties_by_short_name:
            prop = self._properties_by_short_name[name]
        if name in self._properties_by_full_name:
            prop = self._properties_by_full_name[name]
        return prop

    def draw_properties(self, entity_reference: Any, component_to_draw_on: bpy.types.UILayout,
                        property_names: Collection[str] | None, *, text: str | None = None, **kwargs: Any) -> None:
        """
        Draws the specified properties on a Blender UI component.

        Args:
            entity_reference: The Blender entity reference to draw the properties from.
            component_to_draw_on: The Blender UI component (e.g., a box) to draw the properties on.
            property_names: The property names to draw. None or empty means nothing is drawn.
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

    def deferred_draw_property(self, entity_reference: Any, component_to_draw_on: bpy.types.UILayout,
                               property_name: str, text: str | None = None) -> None:
        """Abstract method that can be overridden by subclasses to implement drawing logic for properties which
        are not known to the configset."""
        _LOG.debug("Deferred draw not overridden")


    def get_property_id_for_draw(self, name: str) -> str | None:
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
