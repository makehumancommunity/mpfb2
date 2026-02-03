# DynamicConfigSet

DynamicConfigSet is a subclass of `BlenderConfigSet` for managing configuration when the storage entity is a Blender object with both pre-defined properties and additional dynamic properties that can change at runtime. It supports serialization and deserialization of both property types.

## Source

`src/mpfb/services/dynamicconfigset.py`

## Dependencies

- `LogService` — logging
- `BlenderConfigSet` — parent class
- `bpy` — Blender API

## Public API

### has_key(name, entity_reference=None)

Check if a property exists in either pre-defined or dynamic properties.

### has_key_with_value(name, entity_reference)

Check if a property exists and has a value in either pre-defined or dynamic properties.

### set_value_dynamic(name, value, property_definition, entity_reference)

Set the value of a dynamic property without storing it in the pre-defined list.

### get_value(name, default_value=None, entity_reference=None)

Retrieve a value from pre-defined or dynamic properties.

### get_keys(entity_reference)

Retrieve all short names including both pre-defined and dynamic properties.

### get_fullname_key_from_shortname_key(key_name, entity_reference)

Construct the full property name, handling both pre-defined and dynamic properties.

### get_dynamic_keys(entity_reference)

Retrieve short names of only the dynamic properties.

### from_definitions_in_json_directory(properties_dir, prefix="", dynamic_prefix="", getter_factory=None, setter_factory=None)

Create a `DynamicConfigSet` from JSON definitions in the specified directory. *Static method.*

### deferred_draw_property(entity_reference, component_to_draw_on, property_name, text=None)

Draw dynamic properties that are not registered with the RNA system.

## Example

```python
from mpfb.services.dynamicconfigset import DynamicConfigSet

config = DynamicConfigSet.from_definitions_in_json_directory(
    "/path/to/properties", prefix="obj_", dynamic_prefix="dyn_"
)
config.set_value_dynamic("custom_prop", 1.5, prop_def, entity_reference=obj)
```
