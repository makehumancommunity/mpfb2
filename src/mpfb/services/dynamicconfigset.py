"""
A specific config set for when there are also extra properties which are dynamic and potentially changing continuously.

This config set will work the same as the standard BlenderConfigSet in regards to pre-defined properties.
That is, it will maintain an array of property definitions, which will be read from the entity_reference object in the
same way as in the standard BlenderConfigSet.

On top of this, it will also scan the object for properties with a name starting with the dynamic_prefix. The standard
methods in BlenderConfigSet will be extended to handle these dynamic properties.
"""

import bpy, json, typing, weakref
from collections.abc import Collection
from typing import Any
from .logservice import LogService
from .blenderconfigset import BlenderConfigSet
from ..types import PropertyAccessorFactory, PropertyDefinition

_LOG = LogService.get_logger("configuration.dynamicconfigset")
#_LOG.set_level(LogService.DEBUG)

# Every live DynamicConfigSet, so the handlers below can reach all of their per-entity caches
_CONFIG_SETS = []

# Property reconstructions queued on a timer which have not run yet, so they can be dropped when MPFB is disabled
_PENDING_TIMERS = set()


@bpy.app.handlers.persistent
def _mpfb_clear_dynamic_key_caches(*_args):
    """Drop every cached dynamic key list. Caches are keyed by as_pointer(), which is not valid after file load or undo."""
    for reference in list(_CONFIG_SETS):
        config_set = reference()
        if config_set is None:
            _CONFIG_SETS.remove(reference)
        else:
            config_set._dynamic_keys_cache.clear()


@bpy.app.handlers.persistent
def _mpfb_rebuild_dynamic_properties(*_args):
    """Recreate every dynamic property definition the freshly opened file asks for.

    Dynamic properties are registered at runtime, so a new blender process starts without them. The values are
    in the file, the "$name$" custom properties written by _serialize_property say which definitions to recreate.
    """
    for reference in list(_CONFIG_SETS):
        config_set = reference()
        if config_set is not None and config_set.dynamic_prefix:
            for entity in bpy.data.objects:
                config_set.rebuild_dynamic_properties(entity)


def _remove_handlers() -> None:
    """Takes both handlers out of every list they can be in."""
    names = (_mpfb_clear_dynamic_key_caches.__name__, _mpfb_rebuild_dynamic_properties.__name__)
    for handlers in (bpy.app.handlers.load_post, bpy.app.handlers.undo_post, bpy.app.handlers.redo_post):
        for existing in list(handlers):
            if getattr(existing, "__name__", None) in names:
                handlers.remove(existing)


def register_handlers() -> None:
    """Hook the cache reset and the rebuild of dynamic properties up to file load and undo. Called from MPFB register()."""
    _remove_handlers()
    for handlers in (bpy.app.handlers.load_post, bpy.app.handlers.undo_post, bpy.app.handlers.redo_post):
        handlers.append(_mpfb_clear_dynamic_key_caches)
    # Must come after the cache reset, rebuilding fills the cache again
    bpy.app.handlers.load_post.append(_mpfb_rebuild_dynamic_properties)


def unregister_handlers() -> None:
    """Undo register_handlers() and drop reconstructions still waiting on a timer. Called from MPFB unregister()."""
    _remove_handlers()
    for callback in list(_PENDING_TIMERS):
        if bpy.app.timers.is_registered(callback):
            bpy.app.timers.unregister(callback)
    _PENDING_TIMERS.clear()


class DynamicConfigSet(BlenderConfigSet):

    """Specific management of configuration when the storage entity is an object and there are extra properties
    which are dynamic and changing continuously."""

    def __init__(self, properties: list[PropertyDefinition], prefix: str = "", dynamic_prefix: str | None = None,
                 getter_factory: PropertyAccessorFactory | None = None,
                 setter_factory: PropertyAccessorFactory | None = None) -> None:
        _LOG.debug("Constructing new dynamic config set with prefix, dynamic_prefix", (prefix, dynamic_prefix))
        BlenderConfigSet.__init__(self, properties, bpy.types.Object, prefix, getter_factory=getter_factory, setter_factory=setter_factory)
        # Declared as str, not "str | None", even though the parameter still accepts None. Every method
        # below concatenates this onto a short name, so a None prefix is a TypeError waiting to happen
        # rather than a supported mode; both call sites in the tree supply a prefix.
        self.dynamic_prefix: str = typing.cast(str, dynamic_prefix)
        self._pending_deserialization: set[str] = set()
        # Per-entity cache of _list_object_properties_matching_dynamic_prefix(), as panels ask for the keys on every redraw.
        # Keyed by as_pointer() with the name as a sanity check. Invalidated on add/remove and on file load and undo.
        self._dynamic_keys_cache: dict[int, Any] = {}
        _CONFIG_SETS.append(weakref.ref(self))

    def _invalidate_dynamic_keys_cache(self, entity_reference: bpy.types.Object | None) -> None:
        if entity_reference is not None:
            self._dynamic_keys_cache.pop(entity_reference.as_pointer(), None)

    def _find_property(self, name: str) -> PropertyDefinition | None:
        """Find the definition of a property. Returns None for dynamic properties not known to this config set."""
        prop = super()._find_property(name)
        _LOG.debug("Property from super", prop)
        if prop is not None:
            return prop
        _LOG.debug("Did not find a definition for property", name)
        return None

    def _read_serialized_definition(self, entity_reference: bpy.types.Object, long_name: str) -> PropertyDefinition | None:
        """Read the property definition stored on the entity. Returns None if there is none or it cannot be parsed."""
        serialized_name = f"${long_name}$"
        serialized: Any = None
        for item in entity_reference.items():
            if item[0] == serialized_name:
                serialized = item[1]
                break
        if serialized is None:
            # Properties registered on the blender type are not in the custom properties, read through RNA
            serialized = getattr(entity_reference, serialized_name, None)
        if not serialized:
            return None
        try:
            return json.loads(serialized)
        except Exception as e:
            _LOG.warn("Could not parse the stored definition of a property", (serialized_name, e))
            return None

    def _deserialize_property(self, entity_reference: bpy.types.Object, long_name: str) -> None:
        _LOG.debug("Deserializing property", long_name)
        value: Any = None
        for item in entity_reference.items():
            if item[0] == long_name:
                value = item[1]
                break

        prop_def = self._read_serialized_definition(entity_reference, long_name)
        _LOG.debug("Deserializing property definition, value", (prop_def, value))
        if prop_def is not None:
            if long_name in entity_reference:
                # The following will cause an exception if the state is wrong. We want that, since we want to avoid
                # also trying to set the value later on. This we'll let this exception be raided and
                # we catch it in the caller method
                del entity_reference[long_name]
                _LOG.debug(f"Successfully deleted custom property {long_name}")

            # Add the property with its full definition
            self.add_property(prop_def, override_prefix=self.dynamic_prefix)
            self._invalidate_dynamic_keys_cache(entity_reference)

            # Set the value if we had one. Properties with getter and setter keep their value elsewhere.
            if value is not None:
                if prop_def.get("type") == "enum":
                    value = self._enum_identifier(prop_def, value)
                setattr(entity_reference, long_name, value)
                _LOG.debug(f"Restored value {value} for property {long_name}")

    @staticmethod
    def _enum_identifier(prop_def: PropertyDefinition, value: Any) -> Any:
        """The enum identifier for a value read back from the custom properties.

        Up to blender 4.5 the values of bpy.props properties are stored with the custom properties
        and enum is stored as the number of its item. Enum property refuses that number, so it is turned back into the identifier.
        In 5.0 those values are stored apart and never reach this point.
        """
        if not isinstance(value, int) or isinstance(value, bool):
            return value
        for index, item in enumerate(prop_def.get("items") or []):
            number = item[3] if len(item) > 3 else index
            if number == value:
                return item[0]
        return value

    def _serialize_property(self, entity_reference: bpy.types.Object, short_name: str,
                            property_definition: PropertyDefinition) -> None:
        """Store the property definition on the entity, so that it can be rebuilt after a reload.

        Stored as a plain custom property, since a runtime-registered property does not appear in entity.items() until it is registered again.
        """
        serialized_name = f"${self.dynamic_prefix}{short_name}$"
        serialized_property_def = json.dumps(property_definition)
        entity_reference[serialized_name] = serialized_property_def

    def rebuild_dynamic_properties(self, entity_reference: bpy.types.Object) -> int:
        """Register the definitions of every dynamic property this entity has stored, and return how many.

        Only the definition is recreated, the value is already in the file.
        """
        rebuilt = 0
        for name in [str(key) for key in entity_reference.keys()]:
            if not (name.startswith("$") and name.endswith("$")):
                continue
            long_name = name.strip("$")
            if not long_name.startswith(self.dynamic_prefix):
                continue
            if hasattr(self.get_type(), long_name) and long_name in self._properties_by_full_name:
                continue
            try:
                self._deserialize_property(entity_reference, long_name)
                rebuilt += 1
            except Exception as e:
                _LOG.error("Could not rebuild dynamic property", (long_name, e))
        if rebuilt:
            _LOG.debug("Rebuilt dynamic property definitions", (entity_reference.name, rebuilt))
        return rebuilt

    def _deserialization_timer(self, entity_reference: bpy.types.Object, prop: str) -> None:
        # Missing properties are noticed while drawing, so avoid queueing a reconstruction on every redraw
        if prop in self._pending_deserialization:
            _LOG.trace("Reconstruction is already queued for", prop)
            return
        self._pending_deserialization.add(prop)
        _LOG.info("Will attempt to reconstruct custom property", prop)
        def callback() -> None:
            _LOG.debug("About to execute timed creation", prop)
            try:
                self._deserialize_property(entity_reference, prop)
            except Exception as e:
                _LOG.error("Error deserializing property", (prop, e))
            finally:
                self._pending_deserialization.discard(prop)
                _PENDING_TIMERS.discard(callback)
        _PENDING_TIMERS.add(callback)
        bpy.app.timers.register(callback, first_interval=0.1)

    def _list_object_properties_matching_dynamic_prefix(self, entity_reference: bpy.types.Object | None) -> Collection[str]:
        if self.dynamic_prefix is None:
            _LOG.warn("dynamic_prefix is None in this DynamicConfigSet")
            return []
        if entity_reference is None:
            raise ValueError("Must provide a valid entity reference in order to find dynamic properties")

        pointer = entity_reference.as_pointer()
        cached = self._dynamic_keys_cache.get(pointer)
        if cached is not None and cached[0] == entity_reference.name:
            _LOG.trace("Using cached dynamic key list for", entity_reference.name)
            return cached[1]

        result, is_complete = self._scan_object_properties_matching_dynamic_prefix(entity_reference)
        if is_complete:
            self._dynamic_keys_cache[pointer] = (entity_reference.name, result)
        else:
            # Some properties are still waiting for the deferred timer, caching now would hide them for good
            _LOG.trace("Not caching an incomplete dynamic key list for", entity_reference.name)
        return result

    def _scan_object_properties_matching_dynamic_prefix(self, entity_reference: bpy.types.Object) -> tuple[set[str], bool]:
        """Returns (property names, whether every property was already registered on the type)."""
        prop_names: list[str] = []
        deferred = 0
        # A property registered on the type is visible on every entity of that type
        # only the ones with a definition written to this entity by _serialize_property are its own
        stored = {str(key) for key in entity_reference.keys()}
        for prop in entity_reference.bl_rna.properties:
            if prop.identifier.startswith(self.dynamic_prefix):
                if f"${prop.identifier}$" not in stored:
                    continue
                if hasattr(entity_reference, prop.identifier):
                    value = getattr(entity_reference, prop.identifier)
                    _LOG.trace("Found potential dynamic property", (entity_reference, prop.identifier, value))
                    # An empty string is a valid value (for example an unset texture path)
                    if value is not None:
                        prop_names.append(prop.identifier)
                        # Registered on the type but unknown to this config set (for example after addon reload), rebuild from the entity
                        if prop.identifier not in self._properties_by_full_name and "$" not in prop.identifier:
                            _LOG.debug("Found dynamic property without a known definition", prop.identifier)
                            deferred += 1
                            self._deserialization_timer(entity_reference, prop.identifier)

        # Ensure that dynamic properties are created if they are missing on the type. We can't recreate them
        # in the draw context, so will need to defer the creation with a timer
        for item in entity_reference.items():
            _LOG.trace("item", item)
            prop = item[0]
            if prop.startswith(self.dynamic_prefix) and prop not in prop_names:
                _LOG.debug("Found custom property not on type", prop)
                deferred += 1
                self._deserialization_timer(entity_reference, prop)
            if "$" in prop:
                prop = prop.replace("$", "")
                if prop.startswith(self.dynamic_prefix) and prop not in prop_names:
                    _LOG.debug("Found serialized property still not on type", prop)
                    deferred += 1
                    self._deserialization_timer(entity_reference, prop)

        prop_names.sort()

        return set(prop_names), deferred == 0

    def _is_predefined(self, name: str) -> bool:
        """Whether the name is one of the properties from the json definitions, and not a dynamic one."""
        if not super().has_key(name):
            return False
        prop = self._properties_by_full_name.get(name) or self._properties_by_short_name.get(name)
        if prop is None:
            # Only reachable through an alias, which only defined properties have
            return True
        return not prop["full_name"].startswith(self.dynamic_prefix)

    def has_key(self, name: str, entity_reference: Any = None) -> bool:
        """Checks if the config set contains the provided property name.

        Args:
            name (str): The name of the property to check.
            entity_reference (optional): The Blender entity reference to check for dynamic properties.

        Returns:
            bool: True if the property is found, False otherwise.
        """
        has_key_predefined = self._is_predefined(name)
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

    def has_key_with_value(self, name: str, entity_reference: Any) -> bool:
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

    def set_value_dynamic(self, name: str, value: Any, property_definition: PropertyDefinition,
                          entity_reference: bpy.types.Object | None) -> None:
        """
        Sets the value of a dynamic property in the configuration set, without storing it in the list
        of pre-defined properties.

        Args:
            name (str): The name of the property to set.
            value: The value to set.
            property_definition: The definition dict for the property, in the same shape add_property takes.
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

        # The definition is shared on the blender type, but the serialization has to be written for every entity
        self._serialize_property(entity_reference, name, property_definition)

        # A property can be new for this entity even if the type already knows it
        cached = self._dynamic_keys_cache.get(entity_reference.as_pointer())
        if cached is None or full_dynamic_name not in cached[1]:
            self._invalidate_dynamic_keys_cache(entity_reference)

        existing_value = getattr(entity_reference, full_dynamic_name, None)
        if existing_value is None or isinstance(value, tuple) or isinstance(value, list) or existing_value != value:
            _LOG.debug("Setting property value", (full_dynamic_name, value))
            setattr(entity_reference, full_dynamic_name, value)
        else:
            # This is since both creating all properties and calling the setter method (which potentially calls
            # scene updates etc) can take an unreasonably long time.
            _LOG.debug("Avoiding property set since value is identical to existing value", (value, existing_value))

    def remove_dynamic_key(self, name: str, entity_reference: bpy.types.Object | None) -> None:
        """
        Removes a dynamic property, both the definition on the blender type and what was stored on the entity.

        The definition lives on the type, so other entities keep their serialized definition and the property is recreated for them.

        Args:
            name (str): The name of the dynamic property without the dynamic prefix.
            entity_reference: The Blender entity the property was stored on.
        """
        _LOG.enter()
        if entity_reference is None:
            raise ValueError("Must provide a valid entity reference in order to remove dynamic properties")

        full_dynamic_name = self.dynamic_prefix + name
        serialized_name = f"${full_dynamic_name}$"

        for property_name in [full_dynamic_name, serialized_name]:
            if hasattr(self._bpytype, property_name):
                try:
                    delattr(self._bpytype, property_name)
                except Exception as e:
                    _LOG.warn("Could not remove property from type", (property_name, e))
            if property_name in entity_reference:
                del entity_reference[property_name]

        self._properties_by_full_name.pop(full_dynamic_name, None)
        self._properties_by_short_name.pop(name, None)
        self._invalidate_dynamic_keys_cache(entity_reference)
        _LOG.debug("Removed dynamic property", full_dynamic_name)

    def remove_dynamic_keys_with_prefix(self, prefix: str, entity_reference: bpy.types.Object | None) -> list[str]:
        """
        Removes all dynamic properties whose short name starts with the given prefix.

        Args:
            prefix (str): The start of the short names to match, for example "myasset_".
            entity_reference: The Blender entity the properties were stored on.

        Returns:
            list: The full names of the properties which were removed.
        """
        _LOG.enter()
        if entity_reference is None:
            raise ValueError("Must provide a valid entity reference in order to remove dynamic properties")

        full_prefix = self.dynamic_prefix + prefix
        matches: set[str] = set()

        for prop in entity_reference.bl_rna.properties:
            if prop.identifier.startswith(full_prefix):
                matches.add(prop.identifier)

        for item in entity_reference.items():
            property_name = str(item[0]).replace("$", "")
            if property_name.startswith(full_prefix):
                matches.add(property_name)

        for full_dynamic_name in matches:
            self.remove_dynamic_key(full_dynamic_name[len(self.dynamic_prefix):], entity_reference)

        _LOG.debug("Removed dynamic properties", matches)
        return sorted(matches)

    def get_value(self, name: str, default_value: Any = None, entity_reference: Any = None) -> Any:
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

        # Properties registered on the blender type are not in the custom properties, read through RNA
        if hasattr(self._bpytype, full_dynamic_name):
            value = getattr(entity_reference, full_dynamic_name, None)
            _LOG.debug("Property value read from type", (full_dynamic_name, value))
            if value is not None:
                return value

        # Not registered yet (for example right after loading a file), so read the raw custom property
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

    def get_keys(self, entity_reference: bpy.types.Object | None) -> set[str]:
        """
        Retrieves all the short names of the properties in the configuration set, including dynamic properties.

        Returns:
            set[str]: All the short names of the properties.
        """
        _LOG.enter()
        properties = [name for name in super().get_keys() if self._is_predefined(name)]
        _LOG.debug("Pre-defined properties", properties)
        for prop in self._list_object_properties_matching_dynamic_prefix(entity_reference):
            properties.append(prop.replace(self.dynamic_prefix, ""))
        properties.sort()
        properties = set(properties)
        _LOG.debug("All keys", properties)
        return properties

    def get_fullname_key_from_shortname_key(self, key_name: str, entity_reference: bpy.types.Object | None) -> str:
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

    def get_dynamic_keys(self, entity_reference: bpy.types.Object | None) -> list[str]:
        """
        Retrieves all the short names of the dynamic properties in the configuration set, excluding predefined properties.

        Returns:
            list[str]: All the short names of dynamic properties.
        """
        _LOG.enter()
        properties: list[str] = []
        for prop in self._list_object_properties_matching_dynamic_prefix(entity_reference):
            properties.append(prop.replace(self.dynamic_prefix, ""))
        properties.sort()
        _LOG.debug("All dynamic keys", properties)
        return properties

    @staticmethod
    def from_definitions_in_json_directory(properties_dir: str, prefix: str = "", dynamic_prefix: str = "",
                                           getter_factory: PropertyAccessorFactory | None = None,
                                           setter_factory: PropertyAccessorFactory | None = None) -> "DynamicConfigSet":
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

    def deferred_draw_property(self, entity_reference: Any, component_to_draw_on: bpy.types.UILayout,
                               property_name: str, text: str | None = None, **kwargs: Any) -> None:
        """
        Draw a dynamic property that may not be registered with the RNA system.
        This handles both properties created in the current session and those loaded from a saved file.

        Args:
            entity_reference: The Blender object containing the property
            component_to_draw_on: The UI component to draw on (layout, box, etc.)
            property_name: The name of the property without the dynamic prefix
            text: Optional label text to display
            **kwargs: Additional keyword arguments to pass on to the blender prop() call
        """
        _LOG.debug("In deferred draw for dynamic property", property_name)

        # Check if this is a dynamic property
        if property_name not in self.get_dynamic_keys(entity_reference):
            _LOG.debug("Property not found in dynamic properties", property_name)
            return

        full_property_name = self.dynamic_prefix + property_name

        # Fall back on the definition stored on the entity so that labels and panel toggles still work
        definition = self._read_serialized_definition(entity_reference, full_property_name) or {}

        label = text if text else definition.get("label", property_name)

        if definition.get("subtype", None) == "panel_toggle":
            is_open = self.get_value(property_name, False, entity_reference=entity_reference)
            icon = 'TRIA_DOWN' if is_open else 'TRIA_RIGHT'
            component_to_draw_on.prop(entity_reference, full_property_name, text=label, icon=icon, emboss=True, **kwargs)
            return

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
            component_to_draw_on.prop(entity_reference, f'["{full_property_name}"]', text=label, **kwargs)
        else:
            # For properties added in the current session, use the standard approach
            _LOG.debug("Drawing as standard property", full_property_name)
            component_to_draw_on.prop(entity_reference, full_property_name, text=label, **kwargs)
