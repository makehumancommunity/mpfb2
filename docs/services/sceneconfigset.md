# SceneConfigSet

SceneConfigSet is a subclass of `BlenderConfigSet` specialized for managing configuration settings when the storage entity is a Blender scene. It automatically handles conversion from Blender `Context` to `Scene` objects.

## Source

`src/mpfb/services/sceneconfigset.py`

## Dependencies

- `LogService` — logging
- `BlenderConfigSet` — parent class
- `bpy` — Blender API

## Public API

### check_and_transform_entity_reference(entity_reference)

Validate the entity reference and convert a `Context` to its `Scene` if necessary.

### from_definitions_in_json_directory(properties_dir, prefix="")

Create a `SceneConfigSet` instance from property definitions in the specified directory. *Static method.*

## Example

```python
from mpfb.services.sceneconfigset import SceneConfigSet

config = SceneConfigSet.from_definitions_in_json_directory(
    "/path/to/properties", prefix="mypanel_"
)
config.set_value("detail_level", 3, entity_reference=bpy.context.scene)
```
