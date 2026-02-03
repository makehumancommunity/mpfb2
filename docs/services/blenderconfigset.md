# BlenderConfigSet

BlenderConfigSet is a concrete implementation of `ConfigurationSet` designed to manage configuration settings within Blender. It allows defining, retrieving, setting, and displaying properties on Blender entities with support for multiple property types, aliases, and custom getter/setter factories.

## Source

`src/mpfb/services/blenderconfigset.py`

## Dependencies

- `LogService` — logging
- `ConfigurationSet` — abstract base class
- `bpy` — Blender API and property types (`BoolProperty`, `StringProperty`, `EnumProperty`, `IntProperty`, `FloatProperty`, `FloatVectorProperty`)

## Public API

### get_type()

Return the Blender type this configuration set manages.

### get_fullname_key_from_shortname_key(key_name)

Construct the full property name by combining the prefix with the short name.

### get_definitions_in_json_directory(properties_dir)

Read property definitions from JSON files in the specified directory. *Static method.*

### check_and_transform_entity_reference(entity_reference)

Validate and transform an entity reference to match the expected Blender type.

### get_value(name, default_value=None, entity_reference=None)

Retrieve the value of a property from a Blender entity.

### set_value(name, value, entity_reference=None)

Set the value of a property on a Blender entity.

### get_keys()

Retrieve all short names of properties in the configuration set.

### has_key(name)

Check if a property with the given name exists.

### has_key_with_value(name, entity_reference=None)

Check if a property exists and has a value on the given entity.

### add_property(prop, items_callback=None, override_prefix=None)

Add a new property to the configuration set and define it on the Blender entity type.

### draw_properties(entity_reference, component_to_draw_on, property_names, text=None, **kwargs)

Draw specified properties on a Blender UI component.

### deferred_draw_property(entity_reference, component_to_draw_on, property_name, text=None)

Draw a property not known to the configset (intended for override in subclasses).

### get_property_id_for_draw(name)

Retrieve the full property name for drawing purposes.

## Example

```python
from mpfb.services.blenderconfigset import BlenderConfigSet

config = BlenderConfigSet(bpy.types.Object, prefix="myprefix_")
config.add_property({
    "type": "boolean",
    "name": "enable_feature",
    "description": "Enable the feature",
    "default": True
})
value = config.get_value("enable_feature", entity_reference=some_object)
```
