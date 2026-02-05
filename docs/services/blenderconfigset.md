# BlenderConfigSet

## Overview

BlenderConfigSet is the primary concrete implementation of ConfigurationSet, designed to manage configuration settings by storing them as Blender properties on entity types. It bridges the gap between MPFB's configuration system and Blender's property system, allowing settings to be stored directly on scenes, objects, or other Blender data types.

The class supports multiple property types matching Blender's property system: booleans, strings, integers, floats, enums, colors, vectors, and file/directory paths. Properties can be defined either programmatically or loaded from JSON definition files, making it easy to declare large sets of configuration options.

Each BlenderConfigSet is bound to a specific Blender type (e.g., `bpy.types.Scene` or `bpy.types.Object`) and uses a configurable prefix to namespace its properties. For example, a config set with prefix `"modeling_"` on `bpy.types.Scene` would create properties like `MPFB_modeling_detail_level`. This prevents naming collisions between different MPFB subsystems.

The class also provides UI integration through `draw_properties()`, which renders properties directly in Blender panels with proper labels and formatting. It supports property aliases for backwards compatibility when property names change.

## Source

`src/mpfb/services/blenderconfigset.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("configuration.blenderconfigset")` |
| `ConfigurationSet` | Abstract base class |

## Property Types

Properties are defined as dictionaries with these fields:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Short name (identifier) |
| `type` | Yes | Property type (see below) |
| `description` | Yes | Help text shown in UI |
| `default` | Yes | Default value |
| `items` | Enum only | List of `[identifier, name, description]` tuples |
| `min` / `max` | Float only | Value range constraints |
| `aliases` | No | Alternative names for backwards compatibility |
| `label` | No | Display name in UI (defaults to `name`) |
| `subtype` | No | Special rendering (e.g., `"panel_toggle"` for booleans) |

**Supported types:**
- `boolean` — `BoolProperty`
- `string` — `StringProperty`
- `path` — `StringProperty` with `FILE_PATH` subtype
- `dir_path` — `StringProperty` with `DIR_PATH` subtype
- `int` — `IntProperty`
- `float` — `FloatProperty` with optional min/max
- `vector_location` — `FloatVectorProperty` (3D XYZ)
- `color` — `FloatVectorProperty` (4-component RGBA, 0.0–1.0)
- `enum` — `EnumProperty`

## Public API

### Constructor

#### BlenderConfigSet(properties, bpy_type, prefix="", *, lowercase_prefix=False, getter_factory=None, setter_factory=None)

Create a new configuration set.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `properties` | `list[dict]` | — | List of property definitions |
| `bpy_type` | `type` | — | Blender type to attach properties to (e.g., `bpy.types.Scene`) |
| `prefix` | `str` | `""` | Prefix added after `MPFB_` |
| `lowercase_prefix` | `bool` | `False` | Use lowercase `mpfb_` prefix |
| `getter_factory` | `callable` | `None` | Factory function for custom getters |
| `setter_factory` | `callable` | `None` | Factory function for custom setters |

---

### Static Methods

#### get_definitions_in_json_directory(properties_dir)

Read property definitions from all JSON files in a directory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `properties_dir` | `str` | — | Directory containing JSON definition files |

**Returns:** `list[dict]` — List of property definitions.

**Raises:** `IOError` — If a JSON file cannot be read.

---

### Instance Methods

#### get_type()

Return the Blender type this configuration set manages.

**Returns:** `type` — The `bpy.types` class (e.g., `bpy.types.Scene`).

---

#### get_fullname_key_from_shortname_key(key_name)

Construct the full property name from a short name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `key_name` | `str` | — | Short property name |

**Returns:** `str` — Full property name with prefix (e.g., `"MPFB_modeling_detail_level"`).

---

#### check_and_transform_entity_reference(entity_reference)

Validate that an entity reference matches the expected Blender type.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `entity_reference` | `any` | — | The entity to validate |

**Returns:** The validated entity reference.

**Raises:** `ValueError` — If the reference is `None` or wrong type.

---

#### get_value(name, default_value=None, entity_reference=None)

Retrieve the value of a property from a Blender entity.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | Property name (short or full) |
| `default_value` | `any` | `None` | Value if property not found |
| `entity_reference` | `any` | — | Blender entity to read from |

**Returns:** The property value or `default_value`.

Accepts short names, full names, or aliases.

---

#### set_value(name, value, entity_reference=None)

Set the value of a property on a Blender entity.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | Property name (short or full) |
| `value` | `any` | — | Value to set |
| `entity_reference` | `any` | — | Blender entity to modify |

**Raises:** `ValueError` — If the property doesn't exist.

Also updates any aliases defined for the property.

---

#### get_keys()

Retrieve all short property names.

**Returns:** `dict_keys` — View of short property names.

---

#### has_key(name)

Check if a property exists.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | Property name (short, full, or alias) |

**Returns:** `bool` — `True` if property exists.

---

#### has_key_with_value(name, entity_reference=None)

Check if a property exists and has a non-null value.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | Property name |
| `entity_reference` | `any` | — | Entity to check |

**Returns:** `bool` — `True` if property has a value.

---

#### add_property(prop, items_callback=None, override_prefix=None)

Add a new property to the configuration set.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `prop` | `dict` | — | Property definition dictionary |
| `items_callback` | `callable` | `None` | Dynamic items function for enums |
| `override_prefix` | `str` | `None` | Use this prefix instead of the default |

Registers the property on the Blender type and tracks it internally.

---

#### draw_properties(entity_reference, component_to_draw_on, property_names, *, text=None, **kwargs)

Draw properties on a Blender UI component.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `entity_reference` | `any` | — | Entity with the properties |
| `component_to_draw_on` | `UILayout` | — | Blender layout to draw on |
| `property_names` | `list[str]` | — | Properties to draw |
| `text` | `str` | `None` | Override label for all properties |
| `**kwargs` | | | Additional args passed to `layout.prop()` |

**Raises:** `ValueError` — If entity or component is `None`.

Special handling for `panel_toggle` subtype booleans (shows collapse arrows).

---

#### deferred_draw_property(entity_reference, component_to_draw_on, property_name, text=None)

Draw a property not known to the config set.

Override this in subclasses to handle dynamic properties.

---

#### get_property_id_for_draw(name)

Get the full property name for direct `layout.prop()` calls.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | Short property name |

**Returns:** `str` or `None` — Full property name, or `None` if not found.

---

## Examples

### Creating a Configuration Set from JSON

```python
from mpfb.services.blenderconfigset import BlenderConfigSet
import bpy

# Load property definitions from a directory
props = BlenderConfigSet.get_definitions_in_json_directory("/path/to/props")

# Create config set for scene storage
config = BlenderConfigSet(props, bpy.types.Scene, prefix="modeling_")
```

### Defining Properties Programmatically

```python
from mpfb.services.blenderconfigset import BlenderConfigSet
import bpy

properties = [
    {
        "name": "detail_level",
        "type": "int",
        "description": "Level of mesh detail",
        "default": 3
    },
    {
        "name": "use_smoothing",
        "type": "boolean",
        "description": "Apply smoothing to mesh",
        "default": True
    },
    {
        "name": "render_mode",
        "type": "enum",
        "description": "Rendering mode",
        "default": "SOLID",
        "items": [
            ["SOLID", "Solid", "Solid shading"],
            ["WIREFRAME", "Wireframe", "Wireframe view"],
            ["TEXTURED", "Textured", "Full textures"]
        ]
    }
]

config = BlenderConfigSet(properties, bpy.types.Scene, prefix="render_")
```

### Using the Configuration Set

```python
# Set a value
config.set_value("detail_level", 5, entity_reference=bpy.context.scene)

# Get a value
level = config.get_value("detail_level", entity_reference=bpy.context.scene)

# Check if property exists
if config.has_key("use_smoothing"):
    smoothing = config.get_value("use_smoothing", entity_reference=bpy.context.scene)
```

### Drawing in a Panel

```python
class MY_PT_Panel(bpy.types.Panel):
    bl_label = "My Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        config.draw_properties(
            context.scene,
            layout,
            ["detail_level", "use_smoothing", "render_mode"]
        )
```

### Property Definition JSON File

```json
{
    "name": "skin_color",
    "type": "color",
    "description": "Base skin color for the character",
    "default": [0.8, 0.6, 0.5, 1.0],
    "label": "Skin Color"
}
```
