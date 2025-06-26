"""
A specific config set for when there are also extra properties which are dynamic and potentially changing continuously.

This config set will work the same as the standard BlenderConfigSet in regards to pre-defined properties.
That is, it will maintain an array of property definitions, which will be read from the entity_reference object in the
same way as in the standard BlenderConfigSet.

On top of this, it will also scan the object for properties with a name starting with the dynamic_prefix. The standard
methods in BlenderConfigSet will be extended to handle these dynamic properties.
"""

import bpy
from .logservice import LogService
_LOG = LogService.get_logger("configuration.dynamicconfigset")

from .blenderconfigset import BlenderConfigSet


class DynamicConfigSet(BlenderConfigSet):

    """Specific management of configuration when the storage entity is an object and there are extra properties
    which are dynamic and changing continuously."""

    def __init__(self, properties, prefix="", dynamic_prefix=None):
        _LOG.debug("Constructing new dynamic config set with prefix, dynamic_prefix", (prefix, dynamic_prefix))
        BlenderConfigSet.__init__(self, properties, bpy.types.Object, prefix)
        self.dynamic_prefix = dynamic_prefix

    def _list_object_properties_matching_dynamic_prefix(self, entity_reference):
        prop_names = []
        for prop in entity_reference.bl_rna.properties:
            if prop.identifier.startswith(self.dynamic_prefix):
                if hasattr(entity_reference, prop.identifier):
                    value = getattr(entity_reference, prop.identifier)
                    _LOG.debug("Found potential dynamic property", (entity_reference, prop.identifier, value))
                    if value is not None and value != '':
                        prop_names.append(prop.identifier)

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
        _LOG.debug("Checking for property: name, predefined", (name, has_key_predefined))
        if has_key_predefined:
            return True
        if entity_reference:
            proplist = self._list_object_properties_matching_dynamic_prefix(entity_reference)
            _LOG.debug("Dynamic properties", proplist)
            return self.dynamic_prefix + name in proplist
        return False

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
        if not self.has_key(name, entity_reference=entity_reference):
            return False
        value = self.get_value(name, None, entity_reference=entity_reference)
        _LOG.debug("Has property value", (name, value))
        return not value is None

    def set_value_dynamic(self, name, value, property_definition, entity_reference=None):
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

        full_dynamic_name = self.dynamic_prefix + name

        bpytype = self.get_type()
        if hasattr(bpytype, full_dynamic_name):
            _LOG.debug("Property already exists in the type", (bpytype, full_dynamic_name))
        else:
            setattr(bpytype, full_dynamic_name, property_definition)
            _LOG.debug("Added new property to the type", (bpytype, full_dynamic_name, property_definition))

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
            # This is a pre-defined property
            return super().get_value(name, default_value, entity_reference)

        full_dynamic_name = self.dynamic_prefix + name
        bpytype = self.get_type()

        value = None

        if hasattr(bpytype, full_dynamic_name) and hasattr(entity_reference, full_dynamic_name):
            value = getattr(entity_reference, full_dynamic_name)

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

