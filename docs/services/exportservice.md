# ExportService

## Overview

ExportService provides static methods for staging MPFB characters for export to external applications that do not support Blender-native features such as shape keys, modifiers, and armature-driven mesh deformation.

The typical workflow is:

- Create a deep copy of the character hierarchy with `create_character_copy`.
- Load facial animation targets (visemes, ARKit face units) onto the copy with `load_targets`.
- Propagate those shape keys from the basemesh to child clothes and body proxy meshes with `interpolate_targets`.
- Bake mask and subdivision modifiers—and optionally remove helper geometry—with `bake_modifiers_remove_helpers`.

All methods are static.

**Supported facial animation standards:**

| Standard | Constant | Count |
|----------|----------|-------|
| Microsoft visemes | `MICROSOFT_VISEMES` | 22 shapes |
| Meta visemes | `META_VISEMES` | 15 shapes |
| ARKit face units | `ARKIT_FACEUNITS` | 54 shapes |

The module-level constant `SIGNIFICANT_SHIFT_MINIMUM = 0.0001` is used as a threshold when interpolating shape keys to child meshes and when preserving shape keys through modifier baking. Vertex offsets smaller than this value are considered trivial and are discarded, keeping the resulting mesh data compact.

## Source

`src/mpfb/services/exportservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.exportservice")` |
| `TargetService` | Bulk-loading targets, checking for shape keys, baking targets, and reapplying details |
| `ObjectService` | Duplicating objects, finding relatives, activating objects, and getting child lists |
| `ClothesService` | Resolving absolute MHCLO paths for child meshes during interpolation |
| `Mhclo` | Loading MHCLO vertex correspondence data for shape key interpolation |

## Public API

### Character Copy

#### create_character_copy(source_object, name_suffix="_export_copy", place_in_collection=None)

Creates a deep copy of the character hierarchy, including any rig and all child meshes. The root object and every child get the `name_suffix` appended to their names. When the root is an armature, any Armature modifier on a duplicated child mesh is automatically re-pointed to the new armature so the copy is fully self-contained.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `source_object` | `bpy.types.Object` | — | The source object to copy. Typically the basemesh or the rig. The basemesh is located via `ObjectService.find_object_of_type_amongst_nearest_relatives`. |
| `name_suffix` | `str` | `"_export_copy"` | Suffix appended to the name of every duplicated object |
| `place_in_collection` | `bpy.types.Collection` | `None` | Collection where duplicated objects are placed. If `None`, Blender's default collection is used. |

**Returns:** `bpy.types.Object` — The root object of the duplicated hierarchy (the new rig if a rig is present, otherwise the new basemesh).

**Raises:** `ValueError` if no basemesh can be found among the nearest relatives of `source_object`.

---

### Facial Animation Targets

#### load_targets(basemesh, load_microsoft_visemes=True, load_meta_visemes=False, load_arkit_faceunits=False)

Bulk-loads facial animation shape keys onto the basemesh from the installed target asset packs. Each selected group of targets is added at value `0.0` via `TargetService.bulk_load_targets`. At least one of the flags must be `True` for any targets to be loaded.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh to load targets onto |
| `load_microsoft_visemes` | `bool` | `True` | Load the 22 Microsoft viseme targets |
| `load_meta_visemes` | `bool` | `False` | Load the 15 Meta viseme targets |
| `load_arkit_faceunits` | `bool` | `False` | Load the 54 ARKit face unit targets |

**Returns:** None

**Raises:** Exception from `TargetService.bulk_load_targets` if a required target asset pack is not installed.

---

#### interpolate_targets(basemesh)

Transfers viseme and face-unit shape keys from the basemesh to every child mesh that has an associated MHCLO file. For each child, MHCLO vertex correspondence data (three basemesh vertex indices and barycentric weights per child vertex) is used to compute interpolated offsets. A shape key is only created on the child if at least one vertex offset exceeds `SIGNIFICANT_SHIFT_MINIMUM`; otherwise the shape key is skipped to avoid noise.

Modifiers on the basemesh are temporarily disabled during interpolation to ensure vertex positions are read in rest pose, and then restored afterwards.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh whose shape keys are interpolated to children |

**Returns:** None

---

### Modifier Baking

#### bake_modifiers_remove_helpers(basemesh, bake_masks=False, bake_subdiv=False, remove_helpers=True, also_proxy=True)

Bakes mask and subdivision modifiers into the mesh geometry and optionally removes helper/joint geometry. When the basemesh has shape keys, baking uses a copy-bake-apply-delta strategy (implemented in the private `_apply_modifiers_keep_shapekeys` method): for each shape key a temporary duplicate is created, modifiers are applied, and the resulting vertex deltas versus a modifier-applied Basis mesh become the new shape key data. This preserves all shape keys through modifier application. When no shape keys are present, modifiers are applied directly.

Subdivision modifier levels are set to `render_levels` before baking. Mask modifiers on the `body` vertex group (non-inverted) remove helper geometry from the mesh; if this removal is not baked, `remove_helpers` triggers a vertex-group-based deletion instead.

If `also_proxy=True`, the same mask and subdivision baking is applied to the body proxy mesh (if one exists), without the shape key preservation logic.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh to operate on |
| `bake_masks` | `bool` | `False` | Apply mask modifiers into the mesh geometry |
| `bake_subdiv` | `bool` | `False` | Apply subdivision surface modifiers at render level |
| `remove_helpers` | `bool` | `True` | Delete `HelperGeometry` and `JointCubes` vertex groups and their geometry |
| `also_proxy` | `bool` | `True` | Also apply modifiers on the body proxy mesh, if present |

**Returns:** None

---

## Examples

### Full Export Pipeline

Create a complete export-ready copy with Microsoft visemes and modifier baking:

```python
import bpy
from mpfb.services.exportservice import ExportService

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
ExportService.load_targets(
    export_basemesh,
    load_microsoft_visemes=True,
    load_meta_visemes=False,
    load_arkit_faceunits=True
)

# 4. Transfer shape keys from basemesh to clothes / proxy
ExportService.interpolate_targets(export_basemesh)

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
