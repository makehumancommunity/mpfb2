"""
A specific config set for when there are also extra properties which are dynamic and potentially changing continuously.

This config set will work the same as the standard BlenderConfigSet in regards to pre-defined properties.
That is, it will maintain an array of property definitions, which will be read from the entity_reference object in the
same way as in the standard BlenderConfigSet.

On top of this, it will also scan the object for properties with a name starting with the dynamic_prefix. The standard
methods in BlenderConfigSet will be extended to handle these dynamic properties.
"""

import bpy, json
from bpy.props import StringProperty
from .logservice import LogService
from .blenderconfigset import BlenderConfigSet

_LOG = LogService.get_logger("configuration.dynamicconfigset")
#_LOG.set_level(LogService.DEBUG)


class DynamicConfigSet(BlenderConfigSet):

    """Specific management of configuration when the storage entity is an object and there are extra properties
    which are dynamic and changing continuously."""

    def __init__(self, properties, prefix="", dynamic_prefix=None, getter_factory=None, setter_factory=None):
        _LOG.debug("Constructing new dynamic config set with prefix, dynamic_prefix", (prefix, dynamic_prefix))
        BlenderConfigSet.__init__(self, properties, bpy.types.Object, prefix, getter_factory=getter_factory, setter_factory=setter_factory)
        self.dynamic_prefix = dynamic_prefix

    def _find_property(self, name):
        prop = super()._find_property(name)
        _LOG.debug("Property from super", prop)
        if prop is not None:
            return prop
        if hasattr(self._bpytype, name):
            return getattr(self._bpytype, name)
        if hasattr(self._bpytype, self.dynamic_prefix + name):
            return getattr(self._bpytype, self.dynamic_prefix + name)
        _LOG.debug("Did not find property", name)
        return None

    def _deserialize_property(self, entity_reference, long_name):
        serialized_name = f"${long_name}$"
        _LOG.debug("Deserializing property", serialized_name)
        value = None
        serialized_prop_def = None
        for item in entity_reference.items():
            prop = item[0]
            if prop == long_name:
                value = item[1]
            if prop == serialized_name:
                serialized_prop_def = item[1]
        _LOG.debug("Deserializing property definition, value", (serialized_prop_def, value))
        if serialized_prop_def is not None:
            if long_name in entity_reference:
                # The following will cause an exception if the state is wrong. We want that, since we want to avoid
                # also trying to set the value later on. This we'll let this exception be raided and
                # we catch it in the caller method
                del entity_reference[long_name]
                _LOG.debug(f"Successfully deleted custom property {long_name}")

            # Now deserialize and recreate the property with full definition
            prop_def = json.loads(serialized_prop_def)
            _LOG.debug("Deserialized prop def", prop_def)

            # Add the property with its full definition
            self.add_property(prop_def, override_prefix=self.dynamic_prefix)

            # Set the value if we had one
            if value is not None:
                setattr(entity_reference, long_name, value)
                _LOG.debug(f"Restored value {value} for property {long_name}")

    def _serialize_property(self, entity_reference, short_name, property_definition):
        serialized_name = f"${self.dynamic_prefix}{short_name}$"
        serialized_property_def = json.dumps(property_definition)
        if not hasattr(entity_reference, serialized_name):
            _LOG.debug("Adding new property definition property", serialized_name)
            serialized_property_prop = StringProperty(name=serialized_name, default=serialized_property_def, description=f"serialization of {short_name}")
            setattr(self._bpytype, serialized_name, serialized_property_prop)
        setattr(entity_reference, serialized_name, serialized_property_def)

    def _deserialization_timer(self, entity_reference, prop):
        _LOG.info("Will attempt to reconstruct custom property", prop)
        def callback():
            _LOG.debug("About to execute timed creation", prop)
            try:
                self._deserialize_property(entity_reference, prop)
            except Exception as e:
                _LOG.error("Error deserializing property", (prop, e))
        bpy.app.timers.register(callback, first_interval=0.1)

    def _list_object_properties_matching_dynamic_prefix(self, entity_reference):
        prop_names = []
        if self.dynamic_prefix is None:
            _LOG.warn("dynamic_prefix is None in this DynamicConfigSet")
            return []
        if entity_reference is None:
            raise ValueError("Must provide a valid entity reference in order to find dynamic properties")
        for prop in entity_reference.bl_rna.properties:
            if prop.identifier.startswith(self.dynamic_prefix):
                if hasattr(entity_reference, prop.identifier):
                    value = getattr(entity_reference, prop.identifier)
                    _LOG.debug("Found potential dynamic property", (entity_reference, prop.identifier, value))
                    if value is not None and value != '':
                        prop_names.append(prop.identifier)

        # Ensure that dynamic properties are created if they are missing on the type. We can't recreate them
        # in the draw context, so will need to defer the creation with a timer
        for item in entity_reference.items():
            _LOG.debug("item", item)
            prop = item[0]
            if prop.startswith(self.dynamic_prefix) and prop not in prop_names:
                _LOG.debug("Found custom property not on type", prop)
                self._deserialization_timer(entity_reference, prop)
            if "$" in prop:
                prop = prop.replace("$", "")
                if prop.startswith(self.dynamic_prefix) and prop not in prop_names:
                    _LOG.debug("Found serialized property still not on type", prop)
                    self._deserialization_timer(entity_reference, prop)

        prop_names.sort()
        return prop_names

    def has_key(self, name, entity_reference=None):
        """Checks if the config set contains the provided property name.

        Args:
            name (str): The name of the property to check.
            entity_reference (optional): The Blender entity reference to check for dynamic properties.

        Returns:
            bool: True if the property is found, False otherwise.
        """
        has_key_predefined = super().has_key(name)
        _LOG.debug("Checking for property: name, predefined, entity_reference", (name, has_key_predefined, entity_reference))
        if has_key_predefined:
            return True
        if entity_reference:
            proplist = self._list_object_properties_matching_dynamic_prefix(entity_reference)
            _LOG.debug("Dynamic properties", proplist)
            full_name = self.dynamic_prefix + name
            _LOG.debug("Checking for full name", (full_name, full_name in proplist))
            return full_name in proplist
        else:
            _LOG.debug("No entity reference provided, cannot check dynamic properties")
        return False

    def has_key_with_value(self, name, entity_reference):
        """
        Checks if a property with the given name exists and has a value in the configuration set.

        Args:
            name (str): The name of the property to check.
            entity_reference: The Blender entity reference to check the property value on.

        Returns:
            bool: True if the property exists and has a value, False otherwise.
        """
        _LOG.enter()
        if not self.has_key(name, entity_reference=entity_reference):
            return False
        value = self.get_value(name, None, entity_reference=entity_reference)
        _LOG.debug("Has property value", (name, value))
        return not value is None

    def set_value_dynamic(self, name, value, property_definition, entity_reference):
        """
        Sets the value of a dynamic property in the configuration set, without storing it in the list
        of pre-defined properties.

        Args:
            name (str): The name of the property to set.
            value: The value to set.
            property_definition: The blender property to set on the class, for example a StringProperty.
            entity_reference (optional): The Blender entity reference to set the property value on.
        """
        _LOG.enter()
        if not property_definition:
            _LOG.error("Property definition is required for dynamic property set")
            return

        if entity_reference is None:
            raise ValueError("Must provide a valid entity reference in order to set dynamic properties")

        full_dynamic_name = self.dynamic_prefix + name

        bpytype = self.get_type()
        if hasattr(bpytype, full_dynamic_name):
            _LOG.debug("Property already exists in the type", (bpytype, full_dynamic_name))
        else:
            self.add_property(property_definition, override_prefix=self.dynamic_prefix)
            self._serialize_property(entity_reference, name, property_definition)

        _LOG.debug("Setting property value", (full_dynamic_name, value))
        setattr(entity_reference, full_dynamic_name, value)

    def get_value(self, name, default_value=None, entity_reference=None):
        """
        Retrieves the value of a property from a Blender entity, including dynamic properties.

        Args:
            name (str): The name of the property.
            default_value (optional): The default value to return if the property is not found.
            entity_reference (optional): The Blender entity reference to retrieve the property value from.

        Returns:
            The value of the property, or the default value if the property is not found.
        """
        if not entity_reference:
            _LOG.warn("Entity reference is required in order to actually get a value")
            return default_value

        if super().has_key(name):
            _LOG.debug("Property found in pre-defined properties", name)
            # This is a pre-defined property
            return super().get_value(name, default_value, entity_reference)

        full_dynamic_name = self.dynamic_prefix + name

        value = None

        for items in entity_reference.items():
            prop = items[0]
            if prop == full_dynamic_name:
                value = items[1]
                break

        _LOG.debug("Property value", (full_dynamic_name, value))

        if value is None:
            return default_value

        return value

    def get_keys(self, entity_reference):
        """
        Retrieves all the short names of the properties in the configuration set, including dynamic properties.

        Returns:
            dict_keys: An array with a list of all the short names of the properties.
        """
        _LOG.enter()
        properties = list(super().get_keys())
        _LOG.debug("Pre-defined properties", properties)
        for prop in self._list_object_properties_matching_dynamic_prefix(entity_reference):
            properties.append(prop.replace(self.dynamic_prefix, ""))
        properties.sort()
        _LOG.debug("All keys", properties)
        return properties

    def get_fullname_key_from_shortname_key(self, key_name, entity_reference):
        """
        Constructs the full property name using the prefix and the provided short name,
        taking dynamic properties into account.

        Args:
            key_name (str): The short name of the property.

        Returns:
            str: The full property name with the prefix.
        """
        if key_name in self.get_dynamic_keys(entity_reference):
            return self.dynamic_prefix + key_name
        return self._prefix + key_name

    def get_dynamic_keys(self, entity_reference):
        """
        Retrieves all the short names of the dynamic properties in the configuration set, excluding predefined properties.

        Returns:
            dict_keys: An array with a list of all the short names of dynamic properties.
        """
        _LOG.enter()
        properties = []
        for prop in self._list_object_properties_matching_dynamic_prefix(entity_reference):
            properties.append(prop.replace(self.dynamic_prefix, ""))
        properties.sort()
        _LOG.debug("All dynamic keys", properties)
        return properties

    @staticmethod
    def from_definitions_in_json_directory(properties_dir, prefix="", dynamic_prefix="", getter_factory=None, setter_factory=None):
        """
        Creates a DynamicConfigSet instance from property definitions in a specified directory.
        The JSON files will form "predefined" properties. Use methods on resulting object to
        add dynamic properties.

        Args:
            properties_dir (str): The directory containing JSON files with property definitions.
            prefix (str, optional): A prefix to add to the "predefined" property names.
            dynamic_prefix (str, optional): A prefix to add to the dynamic property names.

        Returns:
            DynamicConfigSet: An instance of DynamicConfigSet with properties loaded from the JSON files.
        """
        known_properties = BlenderConfigSet.get_definitions_in_json_directory(properties_dir)
        return DynamicConfigSet(known_properties, prefix=prefix, dynamic_prefix=dynamic_prefix, getter_factory=getter_factory, setter_factory=setter_factory)

    def deferred_draw_property(self, entity_reference, component_to_draw_on, property_name, text=None):
        """
        Draw a dynamic property that may not be registered with the RNA system.
        This handles both properties created in the current session and those loaded from a saved file.

        Args:
            entity_reference: The Blender object containing the property
            component_to_draw_on: The UI component to draw on (layout, box, etc.)
            property_name: The name of the property without the dynamic prefix
            text: Optional label text to display
        """
        _LOG.debug("In deferred draw for dynamic property", property_name)

        # Check if this is a dynamic property
        if property_name not in self.get_dynamic_keys(entity_reference):
            _LOG.debug("Property not found in dynamic properties", property_name)
            return

        # Set up the label
        label = property_name
        if text:
            label = text

        full_property_name = self.dynamic_prefix + property_name

        # Try to determine if this is a custom property (from a previous session)
        # or a regular property (added in this session)
        is_custom_prop = False

        # Check if it's in the RNA properties
        for prop in entity_reference.bl_rna.properties:
            if prop.identifier == full_property_name:
                is_custom_prop = False
                break
        else:
            # Not found in RNA properties, check if it's in custom properties
            for key, _ in entity_reference.items():
                if key == full_property_name:
                    is_custom_prop = True
                    break

        if is_custom_prop:
            # For custom properties loaded from a file, use this approach
            _LOG.debug("Drawing as custom property", full_property_name)
            component_to_draw_on.prop(entity_reference, f'["{full_property_name}"]', text=label)
        else:
            # For properties added in the current session, use the standard approach
            _LOG.debug("Drawing as standard property", full_property_name)
            component_to_draw_on.prop(entity_reference, full_property_name, text=label)
