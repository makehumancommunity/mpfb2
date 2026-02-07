# SceneConfigSet

## Overview

SceneConfigSet is a specialized subclass of BlenderConfigSet that manages configuration settings stored on Blender scenes. It provides convenience features for scene-based storage, which is the most common configuration pattern in MPFB for panel settings and global options.

The primary enhancement over BlenderConfigSet is automatic handling of Blender Context objects. When you pass a `bpy.types.Context` as the entity reference, SceneConfigSet automatically extracts the `context.scene` for you. This eliminates boilerplate code in operators and panels where the context is readily available but the scene must be extracted.

SceneConfigSet also provides a convenient factory method `from_definitions_in_json_directory()` that combines property loading and instantiation in a single call, which is the typical pattern used throughout MPFB's UI modules.

Most MPFB panels use SceneConfigSet to store their settings. When a user adjusts a slider or checkbox in an MPFB panel, the value is written to a property on `bpy.context.scene`. This means settings persist with the .blend file and can differ between scenes in the same file.

## Source

`src/mpfb/services/sceneconfigset.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("configuration.sceneconfigset")` |
| `BlenderConfigSet` | Parent class providing core functionality |
| `bpy` | `bpy.types.Scene` as the storage type, `bpy.types.Context` for automatic extraction |

## Public API

### Constructor

#### SceneConfigSet(properties, prefix="")

Create a new scene configuration set.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `properties` | `list[dict]` | — | List of property definitions |
| `prefix` | `str` | `""` | Prefix added after `MPFB_` |

Internally calls `BlenderConfigSet.__init__()` with `bpy.types.Scene` as the type.

---

### Static Methods

#### from_definitions_in_json_directory(properties_dir, prefix="")

Create a SceneConfigSet from JSON property definitions in a directory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `properties_dir` | `str` | — | Directory containing JSON definition files |
| `prefix` | `str` | `""` | Prefix added after `MPFB_` |

**Returns:** `SceneConfigSet` — Configured instance with all properties loaded.

This is the standard factory method used throughout MPFB. It reads all `.json` files in the directory, parses their property definitions, and creates a ready-to-use SceneConfigSet.

---

### Instance Methods

#### check_and_transform_entity_reference(entity_reference)

Validate and transform the entity reference, extracting the scene from a Context if provided.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `entity_reference` | `Scene` or `Context` | — | A Blender scene or context |

**Returns:** `bpy.types.Scene` — The validated scene object.

**Raises:** `ValueError` — If the reference is `None` or not a Scene/Context.

This override allows passing `bpy.context` directly instead of `bpy.context.scene`.

---

### Inherited Methods

All methods from BlenderConfigSet are available:
- `get_value(name, default_value=None, entity_reference=None)`
- `set_value(name, value, entity_reference=None)`
- `get_keys()`
- `has_key(name)`
- `has_key_with_value(name, entity_reference=None)`
- `add_property(prop, items_callback=None, override_prefix=None)`
- `draw_properties(entity_reference, component_to_draw_on, property_names, *, text=None, **kwargs)`
- `serialize_to_json(json_file_path, entity_reference=None, exclude_keys=None)`
- `deserialize_from_json(json_file_path, entity_reference=None)`
- `as_dict(entity_reference=None, exclude_keys=None, json_with_overrides=None)`

---

## Examples

### Creating from JSON Directory

```python
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.locationservice import LocationService
import os

# Typical MPFB pattern: load properties from a ui subdirectory
props_dir = os.path.join(os.path.dirname(__file__), "properties")
PANEL_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(
    props_dir,
    prefix="mypanel_"
)
```

### Using Context Instead of Scene

```python
# With SceneConfigSet, you can pass context directly
class MY_OT_Operator(bpy.types.Operator):
    def execute(self, context):
        # These are equivalent:
        value1 = PANEL_PROPERTIES.get_value("setting", entity_reference=context)
        value2 = PANEL_PROPERTIES.get_value("setting", entity_reference=context.scene)

        return {'FINISHED'}
```

### Panel Implementation Pattern

```python
from mpfb.services.sceneconfigset import SceneConfigSet
import os

# Load properties at module level
_PROPS_DIR = os.path.join(os.path.dirname(__file__), "properties")
PANEL_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(
    _PROPS_DIR,
    prefix="modeling_"
)

class MPFB_PT_ModelingPanel(bpy.types.Panel):
    bl_label = "Modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MPFB"

    def draw(self, context):
        layout = self.layout

        # Draw all panel properties
        PANEL_PROPERTIES.draw_properties(
            context.scene,
            layout,
            ["detail_level", "smoothing_iterations", "preserve_volume"]
        )
```

### Saving and Loading Presets

```python
def save_preset(context, preset_path):
    PANEL_PROPERTIES.serialize_to_json(
        preset_path,
        entity_reference=context.scene,
        exclude_keys=["internal_state"]
    )

def load_preset(context, preset_path):
    PANEL_PROPERTIES.deserialize_from_json(
        preset_path,
        entity_reference=context.scene
    )
```

### Property JSON File Structure

Properties are typically defined in separate JSON files within a `properties/` subdirectory:

**properties/detail_level.json:**
```json
{
    "name": "detail_level",
    "type": "int",
    "description": "Subdivision level for mesh detail",
    "default": 2,
    "min": 0,
    "max": 6,
    "label": "Detail Level"
}
```

**properties/preserve_volume.json:**
```json
{
    "name": "preserve_volume",
    "type": "boolean",
    "description": "Maintain mesh volume during smoothing",
    "default": true,
    "label": "Preserve Volume"
}
```
