# ExportService

## Overview

ExportService provides static methods for staging MPFB characters for export to external applications that do not support Blender-native features such as shape keys, modifiers, and armature-driven mesh deformation.

The typical workflow is:

- Create a deep copy of the character hierarchy with `create_character_copy`.
- Load facial animation targets (visemes, ARKit face units) onto the copy with `FaceService.load_targets`.
- Propagate those shape keys from the basemesh to child clothes and body proxy meshes with `FaceService.interpolate_targets`.
- Bake mask and subdivision modifiers—and optionally remove helper geometry—with `bake_modifiers_remove_helpers`.

All methods are static.

Viseme and face unit loading and interpolation is handled by `FaceService`. ExportService imports the facial animation constants (`MICROSOFT_VISEMES`, `META_VISEMES`, `ARKIT_FACEUNITS`, `SIGNIFICANT_SHIFT_MINIMUM`) from `FaceService` so that `bake_modifiers_remove_helpers` can identify which shape keys are facial-animation-related versus modelling targets.

## Source

`src/mpfb/services/exportservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.exportservice")` |
| `TargetService` | Checking for shape keys, baking targets, and reapplying details |
| `ObjectService` | Duplicating objects, finding relatives, activating objects, and getting child lists |
| `FaceService` | Provides the `MICROSOFT_VISEMES`, `META_VISEMES`, `ARKIT_FACEUNITS` and `SIGNIFICANT_SHIFT_MINIMUM` module constants |

## Module-Level Types

| Name | Definition | Description |
|------|------------|-------------|
| `VertexDelta` | `tuple[int, float, float, float]` | One significant vertex shift inside a shape key: `(vertex index, dx, dy, dz)`. Only shifts longer than `SIGNIFICANT_SHIFT_MINIMUM` are recorded. |
| `ShapeKeyDeltas` | `tuple[str, float, list[VertexDelta]]` | One rebuilt shape key: its name, its value, and the vertex shifts that make it up. |
| `ShapeKeySnapshot` | `TypedDict` with `name: str` and `value: float` | The metadata kept for one shape key while its mesh is rebuilt under it. A `TypedDict` rather than a plain `dict[str, Any]` because the two keys carry different types and both are read back into positions that require the concrete one: the name into `Object.shape_key_add()` and the value into `ShapeKey.value`. |

All three describe the internals of `_apply_modifiers_keep_shapekeys` and are not part of the service's
calling contract.

## Public API

### Character Copy

#### create_character_copy(source_object, name_suffix="_export_copy", place_in_collection=None)

Creates a deep copy of the character hierarchy, including any rig and all child meshes. The root object and every child get the `name_suffix` appended to their names. When the root is an armature, any Armature modifier on a duplicated child mesh is automatically re-pointed to the new armature so the copy is fully self-contained.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `source_object` | `bpy.types.Object \| None` | — | The source object to copy. Typically the basemesh or the rig. The basemesh is located via `ObjectService.find_object_of_type_amongst_nearest_relatives`, which accepts `None` and returns `None` for it, so passing `None` raises the `ValueError` below rather than failing earlier. |
| `name_suffix` | `str` | `"_export_copy"` | Suffix appended to the name of every duplicated object |
| `place_in_collection` | `bpy.types.Collection \| None` | `None` | Collection where duplicated objects are placed. If `None`, Blender's default collection is used. |

**Returns:** `bpy.types.Object` — The root object of the duplicated hierarchy (the new rig if a rig is present, otherwise the new basemesh).

**Raises:** `ValueError` if no basemesh can be found among the nearest relatives of `source_object`,
which includes the case where `source_object` is itself `None`.

The return type is non-optional even though `ObjectService.duplicate_blender_object()` is declared
`bpy.types.Object | None`: that method returns `None` only when handed `None`, and neither call inside this
one can, so both results are narrowed with a `typing.cast`.

---

### Modifier Baking

#### bake_modifiers_remove_helpers(basemesh, bake_masks=False, bake_subdiv=False, remove_helpers=True, also_proxy=True)

Bakes mask and subdivision modifiers into the mesh geometry and optionally removes helper/joint geometry. When the basemesh has shape keys, baking uses a copy-bake-apply-delta strategy (implemented in the private `_apply_modifiers_keep_shapekeys` method): for each shape key a temporary duplicate is created, modifiers are applied, and the resulting vertex deltas versus a modifier-applied Basis mesh become the new shape key data on the final mesh. This preserves all shape keys through modifier application. When no shape keys are present, modifiers are applied directly.

Subdivision modifier levels are set to `render_levels` before baking, but only when `bake_subdiv` is
`True`; without it the SUBSURF modifiers are left exactly as they are, on the basemesh and on the proxy
alike. Mask modifiers on the `body` vertex group (non-inverted) remove helper geometry from the mesh; if this removal is not baked, `remove_helpers` triggers a vertex-group-based deletion instead.

If `also_proxy=True`, the same mask and subdivision baking is applied to the body proxy mesh (if one exists), without the shape key preservation logic.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh to operate on |
| `bake_masks` | `bool` | `False` | Apply mask modifiers into the mesh geometry |
| `bake_subdiv` | `bool` | `False` | Apply subdivision surface modifiers at render level |
| `remove_helpers` | `bool` | `True` | Delete `HelperGeometry` and `JointCubes` vertex groups and their geometry |
| `also_proxy` | `bool` | `True` | Also apply modifiers on the body proxy mesh, if present |

**Returns:** None

Two of the `also_proxy` paths return early — when no `Proxymeshes` object is found among the basemesh's
nearest relatives, and when the proxy has no mask or subdivision modifiers to bake. Both log at debug level
and leave the character's root object active and solely selected, which is the same state the method ends in
normally, so neither is observable to a caller.

---

## Examples

### Full Export Pipeline

Create a complete export-ready copy with Microsoft visemes and modifier baking:

```python
import bpy
from mpfb.services.exportservice import ExportService
from mpfb.services.faceservice import FaceService

# Assume `basemesh` is the selected MPFB basemesh
basemesh = bpy.context.active_object

# 1. Duplicate the full character hierarchy
export_root = ExportService.create_character_copy(
    basemesh,
    name_suffix="_export",
    place_in_collection=bpy.data.collections.get("Export")
)

# 2. Find the duplicated basemesh among the new root's children
from mpfb.services.objectservice import ObjectService
export_basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(export_root)

# 3. Load facial animation shape keys
FaceService.load_targets(
    export_basemesh,
    load_microsoft_visemes=True,
    load_meta_visemes=False,
    load_arkit_faceunits=True
)

# 4. Transfer shape keys from basemesh to clothes / proxy
FaceService.interpolate_targets(export_basemesh)

# 5. Bake modifiers and remove helper geometry
ExportService.bake_modifiers_remove_helpers(
    export_basemesh,
    bake_masks=True,
    bake_subdiv=True,
    remove_helpers=True,
    also_proxy=True
)
```

### Minimal Copy Without Shape Keys

For a simple character with no facial animation requirements:

```python
import bpy
from mpfb.services.exportservice import ExportService

basemesh = bpy.context.active_object

# Duplicate and immediately bake helpers away
export_root = ExportService.create_character_copy(basemesh, name_suffix="_game")

from mpfb.services.objectservice import ObjectService
export_basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(export_root)

ExportService.bake_modifiers_remove_helpers(
    export_basemesh,
    bake_masks=True,
    remove_helpers=True,
    also_proxy=False
)
```
