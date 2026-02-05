# DynamicConfigSet

## Overview

DynamicConfigSet is a specialized subclass of BlenderConfigSet designed for scenarios where configuration properties need to be created at runtime. Unlike BlenderConfigSet and SceneConfigSet, which work with a fixed set of pre-defined properties, DynamicConfigSet can discover and manage properties that are added dynamically during execution.

The class is specifically designed for `bpy.types.Object` storage and distinguishes between two categories of properties: **pre-defined properties** (declared in JSON files or at construction time) and **dynamic properties** (created at runtime with a special prefix). Both types can be accessed through the same interface, and the class handles the complexity of tracking which properties exist on which objects.

The class also handles persistence across Blender sessions. When a .blend file is saved and reopened, dynamic properties that were stored as custom properties need to be reconstructed with their full Blender property definitions. DynamicConfigSet uses a serialization mechanism (storing property definitions in special `$propname$` custom properties) and deferred timer-based reconstruction to handle this transparently.

The main use case for DynamicConfigSet are the hair/fur editor. As dynamic config is complex and fragile, 
**it is generally recommended to avoid using this approach**. If at all possible, use the static approach instead.

## Source

`src/mpfb/services/dynamicconfigset.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("configuration.dynamicconfigset")` |
| `BlenderConfigSet` | Parent class for core functionality |

## Dual-Prefix System

DynamicConfigSet uses two separate prefixes:

| Prefix | Applied To | Example |
|--------|------------|---------|
| Standard prefix | Pre-defined properties | `MPFB_morph_weight` |
| Dynamic prefix | Runtime-created properties | `MPFB_TGT_age_young` |

This separation allows the class to identify which properties were defined at construction time versus created dynamically.

## Public API

### Constructor

#### DynamicConfigSet(properties, prefix="", dynamic_prefix=None, getter_factory=None, setter_factory=None)

Create a new dynamic configuration set.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `properties` | `list[dict]` | — | List of pre-defined property definitions |
| `prefix` | `str` | `""` | Prefix for pre-defined properties (after `MPFB_`) |
| `dynamic_prefix` | `str` | `None` | Prefix for dynamic properties |
| `getter_factory` | `callable` | `None` | Factory for custom property getters |
| `setter_factory` | `callable` | `None` | Factory for custom property setters |

---

### Static Methods

#### from_definitions_in_json_directory(properties_dir, prefix="", dynamic_prefix="", getter_factory=None, setter_factory=None)

Create a DynamicConfigSet from JSON property definitions.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `properties_dir` | `str` | — | Directory containing JSON definition files |
| `prefix` | `str` | `""` | Prefix for pre-defined properties |
| `dynamic_prefix` | `str` | `""` | Prefix for dynamic properties |
| `getter_factory` | `callable` | `None` | Factory for custom getters |
| `setter_factory` | `callable` | `None` | Factory for custom setters |

**Returns:** `DynamicConfigSet` — Configured instance.

---

### Instance Methods

#### has_key(name, entity_reference=None)

Check if a property exists in pre-defined or dynamic properties.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | Property name (short form) |
| `entity_reference` | `Object` | `None` | Object to check for dynamic properties |

**Returns:** `bool` — `True` if property exists.

Unlike the parent class, this method can check for dynamic properties when an entity reference is provided.

---

#### has_key_with_value(name, entity_reference)

Check if a property exists and has a value.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | Property name |
| `entity_reference` | `Object` | — | Object to check |

**Returns:** `bool` — `True` if property has a non-null value.

---

#### get_value(name, default_value=None, entity_reference=None)

Retrieve a property value from pre-defined or dynamic properties.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | Property name (short form) |
| `default_value` | `any` | `None` | Value if not found |
| `entity_reference` | `Object` | — | Object to read from |

**Returns:** Property value or `default_value`.

First checks pre-defined properties, then scans for dynamic properties with the dynamic prefix.

---

#### set_value_dynamic(name, value, property_definition, entity_reference)

Set a dynamic property, creating it if necessary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | Property name (without prefix) |
| `value` | `any` | — | Value to set |
| `property_definition` | `dict` | — | Full property definition (type, description, default, etc.) |
| `entity_reference` | `Object` | — | Object to modify |

This is the primary method for creating and updating dynamic properties. If the property doesn't exist, it creates both the Blender property and a serialized definition for persistence.

The method optimizes by skipping the setter call when the value hasn't changed, which is important for performance when many dynamic properties exist.

---

#### get_keys(entity_reference)

Retrieve all property names (pre-defined and dynamic).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `entity_reference` | `Object` | — | Object to scan for dynamic properties |

**Returns:** `set[str]` — All short property names.

Note: Unlike the parent class, this requires an entity reference to discover dynamic properties.

---

#### get_dynamic_keys(entity_reference)

Retrieve only dynamic property names.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `entity_reference` | `Object` | — | Object to scan |

**Returns:** `list[str]` — Short names of dynamic properties only.

---

#### get_fullname_key_from_shortname_key(key_name, entity_reference)

Get the full property name, using the appropriate prefix.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `key_name` | `str` | — | Short property name |
| `entity_reference` | `Object` | — | Object for dynamic property lookup |

**Returns:** `str` — Full property name with correct prefix.

---

#### deferred_draw_property(entity_reference, component_to_draw_on, property_name, text=None)

Draw a dynamic property in the UI.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `entity_reference` | `Object` | — | Object with the property |
| `component_to_draw_on` | `UILayout` | — | Layout to draw on |
| `property_name` | `str` | — | Short property name |
| `text` | `str` | `None` | Override label |

Handles both properties registered with RNA (created in current session) and custom properties loaded from a saved file.

---

## Examples

### Creating a DynamicConfigSet

```python
from mpfb.services.dynamicconfigset import DynamicConfigSet
import os

props_dir = os.path.join(os.path.dirname(__file__), "properties")
MORPH_PROPERTIES = DynamicConfigSet.from_definitions_in_json_directory(
    props_dir,
    prefix="morph_",
    dynamic_prefix="MPFB_TGT_"
)
```

### Adding Dynamic Properties at Runtime

```python
# Define a new morph target slider
target_def = {
    "name": "age_young",
    "type": "float",
    "description": "Youthful facial features",
    "default": 0.0,
    "min": 0.0,
    "max": 1.0
}

# Create and set the property on an object
MORPH_PROPERTIES.set_value_dynamic(
    "age_young",
    0.5,
    target_def,
    entity_reference=human_object
)
```

### Reading All Morphs from an Object

```python
# Get all morph values for export
all_keys = MORPH_PROPERTIES.get_keys(human_object)
morph_data = {}

for key in MORPH_PROPERTIES.get_dynamic_keys(human_object):
    value = MORPH_PROPERTIES.get_value(key, 0.0, entity_reference=human_object)
    if value != 0.0:
        morph_data[key] = value
```

### Drawing Dynamic Properties in a Panel

```python
class MPFB_PT_MorphPanel(bpy.types.Panel):
    bl_label = "Morphs"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj is None:
            return

        # Draw pre-defined properties
        MORPH_PROPERTIES.draw_properties(
            obj,
            layout,
            ["weight_multiplier", "apply_symmetry"]
        )

        # Draw dynamic target sliders
        layout.separator()
        layout.label(text="Targets:")

        for target_name in MORPH_PROPERTIES.get_dynamic_keys(obj):
            MORPH_PROPERTIES.draw_properties(
                obj,
                layout,
                [target_name]
            )
```

### Getter/Setter Factories for Custom Behavior

```python
def make_getter(config_set, prop_name):
    def getter(self):
        # Custom logic when property is read
        value = self.get(f"MPFB_TGT_{prop_name}", 0.0)
        return value
    return getter

def make_setter(config_set, prop_name):
    def setter(self, value):
        # Trigger shape key update when property changes
        self[f"MPFB_TGT_{prop_name}"] = value
        update_shape_keys(self, prop_name, value)
    return setter

config = DynamicConfigSet.from_definitions_in_json_directory(
    props_dir,
    dynamic_prefix="MPFB_TGT_",
    getter_factory=make_getter,
    setter_factory=make_setter
)
```

## Persistence Mechanism

When a dynamic property is created, DynamicConfigSet stores two things:

1. **The property value** — stored as a Blender property on the object
2. **The property definition** — stored as a JSON string in a custom property named `$MPFB_TGT_propname$`

When a .blend file is reopened, the Blender property definitions are lost (they only exist in memory), but the custom property values remain. DynamicConfigSet detects this situation and uses `bpy.app.timers` to defer reconstruction of the full property definitions, restoring the UI sliders and proper property behavior.
