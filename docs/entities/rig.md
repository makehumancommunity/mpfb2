# Rig

## Overview

`Rig` is the central entity for armature serialisation and deserialisation in MPFB. It provides a full round-trip between a JSON rig definition file and a live Blender armature object.

**Import path (JSON → Blender):** Load a rig definition with `from_json_file_and_basemesh`, then call `create_armature_and_fit_to_basemesh` to build and position the armature in the scene. Internally, this calls `create_bones` (which invokes `get_best_location_from_strategy` for every bone end), `update_edit_bone_metadata` (parent/connect/inherit flags), and `rigify_metadata` (rigify type strings and parameters).

**Export path (Blender → JSON):** Load an existing armature with `from_given_basemesh_and_armature` or `from_given_armature_context`, which calls `add_data_bone_info`, `add_edit_bone_info`, and `add_pose_bone_info` to populate `rig_definition`, then `match_bone_positions_with_strategies` to replace raw coordinates with strategy dicts.

**Positioning strategy system:** Each bone end stores a named strategy that determines how its 3-D world position is resolved at fit time. Supported strategies are:

| Strategy | Resolution |
|----------|-----------|
| `CUBE` | Mean position of a named joint vertex group on the basemesh |
| `VERTEX` | Position of a single basemesh vertex |
| `MEAN` | Mean position of two basemesh vertices |
| `XYZ` | One vertex per axis channel (used for Rigify heel markers) |
| `DEFAULT` | Falls back to the stored `default_position` coordinate |

`get_best_location_from_strategy` resolves the actual `[x, y, z]` coordinate using cached KD-trees built by `build_basemesh_position_info`.

**Parent-child rig concept:** Subrigs reference a parent `Rig` via the `parent` keyword argument. This is used when resolving cross-rig constraint targets using the `JOINTS` strategy, where the subtarget bone in the parent armature is located by tracing joint-cube head/tail pairs.

**Schema versioning:** `_upgrade_definition` handles JSON schema migration (version 100 → 110). The main change in version 110 is the replacement of integer Rigify layer indices with named bone collection references.

Private helper methods (prefixed `_`) handle tasks such as constraint encoding/decoding, KD-tree caching, roll alignment, JOINTS strategy resolution, and bendy-bone serialisation. They are not part of the public API.

For the JSON file format this entity reads and writes, see the [Rig definition file format](../fileformats/rig.md).

## Source

`src/mpfb/entities/rig.py`

## Dependencies

- **Blender:** `bpy`, `bmesh`
- **Math:** `math`, `random`, `typing`, `re`, `mathutils` (`Vector`, `Matrix`, `Euler`, `Quaternion`, `KDTree`), `bl_math.lerp`, `itertools.accumulate`
- **MPFB services:** `LogService`, `ObjectService`, `RigService`
- **MPFB entities:** `GeneralObjectProperties`

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `basemesh` | `bpy.types.Object` | The mesh object the armature deforms |
| `armature_object` | `bpy.types.Object` or `None` | The Blender armature object; `None` until `create_armature_and_fit_to_basemesh` is called |
| `parent` | `Rig` or `None` | Parent rig for subrigs; used in cross-rig constraint resolution |
| `position_info` | `dict` | Cache of vertex coordinates and joint-cube centre locations built by `build_basemesh_position_info` |
| `rig_definition` | `dict` | Per-bone data: head/tail positions, strategies, roll, constraints, rigify parameters |
| `rig_header` | `dict` | File-level metadata: format version, bone collections, `scale_factor`, `extra_bones`, rigify UI |
| `lowest_point` | `float` | Minimum Z coordinate among all basemesh vertices |
| `bad_constraint_targets` | `set` | Bone names whose constraint targets could not be resolved during export |
| `relative_scale` | `float` | Scale factor relative to the parent rig |

## Public API

### Factory methods (static)

---

**`from_json_file_and_basemesh(filename, basemesh, *, parent=None)`**

Create and populate a `Rig` from a JSON rig file and a basemesh object.

| Argument | Type | Description |
|----------|------|-------------|
| `filename` | `str` | Path to the JSON rig definition file |
| `basemesh` | `bpy.types.Object` | The mesh object the armature will deform |
| `parent` | `Rig` or `None` | Parent rig, required if loading a subrig |

**Returns:** `Rig` — the populated instance with `build_basemesh_position_info` already called.

---

**`from_given_armature_context(armature_object, *, is_subrig=None, operator=None, empty=False, fast_positions=False, rigify_ui=False)`**

Create a `Rig` from the active armature in the current scene context. Automatically detects whether the armature is a subrig and constructs a parent rig if needed.

| Argument | Type | Description |
|----------|------|-------------|
| `armature_object` | `bpy.types.Object` or `None` | The armature to export; `None` returns `None` |
| `is_subrig` | `bool` or `None` | Override subrig detection if provided |
| `operator` | operator or `None` | Blender operator instance used for error reporting |
| `empty` | `bool` | If `True`, skip bone data extraction (returns a skeleton `Rig` with only position info) |
| `fast_positions` | `bool` | If `True`, use fast strategy matching (skips edit-bone roll and saved-strategy restore) |
| `rigify_ui` | `bool` | If `True`, also extract Rigify UI state |

**Returns:** `Rig` or `None` — `None` if no mesh context can be found.

---

**`from_given_basemesh_and_armature(basemesh, armature, *, parent=None, empty=False, fast_positions=False, rigify_ui=False)`**

Create a `Rig` from an explicit basemesh and armature object pair. The armature must be the active object in the scene context unless `fast_positions=True`.

| Argument | Type | Description |
|----------|------|-------------|
| `basemesh` | `bpy.types.Object` | The mesh the armature deforms |
| `armature` | `bpy.types.Object` | The armature object to export |
| `parent` | `Rig` or `None` | Parent rig for subrigs |
| `empty` | `bool` | Skip bone data extraction |
| `fast_positions` | `bool` | Use fast strategy matching |
| `rigify_ui` | `bool` | Also extract Rigify UI state |

**Returns:** `Rig` — the populated instance.

---

### Import — JSON → Blender

---

**`create_armature_and_fit_to_basemesh(for_developer=False, add_modifier=True)`**

Build the Blender armature object from `rig_definition`, fit it to the basemesh, and optionally attach an armature modifier.

| Argument | Type | Description |
|----------|------|-------------|
| `for_developer` | `bool` | If `True`, also call `save_strategies` to persist strategy data on bones |
| `add_modifier` | `bool` | If `True`, add or update the armature modifier on the basemesh |

**Returns:** `bpy.types.Object` — the newly created armature object (also stored in `self.armature_object`).

---

**`get_best_location_from_strategy(head_or_tail_info, use_default=True)`**

Resolve a strategy dict to a world-space `[x, y, z]` coordinate by querying the cached KD-trees.

| Argument | Type | Description |
|----------|------|-------------|
| `head_or_tail_info` | `dict` | Strategy dict with keys `strategy`, and strategy-specific keys (`cube_name`, `vertex_index`, or `vertex_indices`) plus an optional `offset` |
| `use_default` | `bool` | If `True` and the strategy cannot be resolved, fall back to `default_position` |

**Returns:** `list[float]` or `None` — `[x, y, z]` world position, or `None` if unresolvable and `use_default=False`.

---

**`create_bone_collections()`**

Create Blender bone collections on the armature from the `collections` list in `rig_header`, replacing any existing collections.

**Returns:** `None`

---

**`create_bones()`**

Create all edit bones from `rig_definition`, set head/tail positions using `get_best_location_from_strategy`, and apply roll values and roll strategies.

**Returns:** `None`

---

**`reposition_edit_bone(*, developer=False)`**

Refit all bones to the current state of the basemesh by reapplying strategies. Also resets `STRETCH_TO`, `CHILD_OF`, and `ARMATURE` constraint state as needed.

| Argument | Type | Description |
|----------|------|-------------|
| `developer` | `bool` | If `True`, also rebuild ARMATURE constraint vertex targets for subrigs |

**Returns:** `None`

---

**`update_edit_bone_metadata()`**

Set parent, `use_connect`, `use_local_location`, `use_inherit_rotation`, `inherit_scale`, bone collection assignments, and bendy-bone parameters on all edit bones.

**Returns:** `None`

---

**`rigify_metadata()`**

Switch to Pose mode and apply `rotation_mode`, constraints, `rigify_type`, and `rigify_parameters` to all pose bones from `rig_definition`.

**Returns:** `None`

---

### Export — Blender → JSON

---

**`build_basemesh_position_info(take_shape_keys_into_account=True)`**

Populate `position_info` with all basemesh vertex coordinates and joint-cube centre positions. Builds the KD-trees lazily used by `find_closest_cube` and `find_closest_vertex`. Respects active shape keys when computing positions.

| Argument | Type | Description |
|----------|------|-------------|
| `take_shape_keys_into_account` | `bool` | If `True`, evaluate a mixed shape key to get deformed vertex positions |

**Returns:** `None`

---

**`add_data_bone_info()`**

Extract head/tail positions, parent, connect flags, inheritance flags, bone collections, and bendy-bone data from the armature's data layer bones and store them in `rig_definition`.

**Returns:** `None`

---

**`add_edit_bone_info()`**

Extract roll values and roll-strategy custom properties from the armature's edit bones. Must be called while the armature is in Edit mode.

**Returns:** `None`

---

**`add_pose_bone_info()`**

Extract `rotation_mode`, constraints, and Rigify metadata from the armature's pose bones.

**Returns:** `None`

---

**`cleanup_float_values()`**

Round all float values in `rig_definition` (positions, roll, offsets) to 5 decimal places to reduce noise when re-saving.

**Returns:** `None`

---

### Developer / strategy tools

---

**`save_strategies(refit=False)`**

Persist the current strategy data from `rig_definition` into bone custom properties (developer mode). Optionally skips writing edit-bone roll strategy properties.

| Argument | Type | Description |
|----------|------|-------------|
| `refit` | `bool` | If `True`, skip saving edit-bone roll strategies |

**Returns:** `None`

---

**`match_bone_positions_with_strategies(fast=False)`**

For every bone head and tail in `rig_definition`, search for the best positioning strategy (CUBE, VERTEX, or MEAN) and update the strategy dict.

| Argument | Type | Description |
|----------|------|-------------|
| `fast` | `bool` | If `True`, skip MEAN strategy search (faster but less precise) |

**Returns:** `None`

---

**`restore_saved_strategies()`**

Compare previously saved strategies (stored in bone custom properties) against the auto-detected strategies and apply the saved ones where they are at least as accurate.

**Returns:** `None`

---

**`list_unmatched_bones()`**

List bone names that still use the fallback `DEFAULT` strategy for their head or tail position.

**Returns:** `list[str]` — bone names with unresolved positioning strategies.

---

**`move_basemesh_if_needed()`**

Translate the basemesh so that its lowest vertex rests at Z = 0, then apply the transform. Only moves if `lowest_point < -0.0001`.

**Returns:** `None`

---

### Spatial queries

---

**`find_closest_cube(pos, max_allowed_dist=0.01)`**

KD-tree search for the nearest joint cube to a world-space position.

| Argument | Type | Description |
|----------|------|-------------|
| `pos` | sequence of 3 floats | World-space `[x, y, z]` to search from |
| `max_allowed_dist` | `float` or `None` | Maximum search radius; `None` disables the distance limit |

**Returns:** `tuple[str, float]` — `(cube_name, distance)`, or `(None, None)` if no cube is within range.

---

**`find_closest_vertex(pos, max_allowed_dist=0.01)`**

KD-tree search for the nearest basemesh vertex to a world-space position.

| Argument | Type | Description |
|----------|------|-------------|
| `pos` | sequence of 3 floats | World-space `[x, y, z]` to search from |
| `max_allowed_dist` | `float` or `None` | Maximum search radius; `None` disables the distance limit |

**Returns:** `tuple[int, float]` — `(vertex_index, distance)`, or `(None, None)` if no vertex is within range.

---

**`find_closest_vertex_mean(pos, max_allowed_dist=0.02, search_radius=None)`**

Find the pair of basemesh vertices whose mean position is closest to the given world-space coordinate.

| Argument | Type | Description |
|----------|------|-------------|
| `pos` | sequence of 3 floats | World-space `[x, y, z]` to search from |
| `max_allowed_dist` | `float` | Maximum mean distance to accept |
| `search_radius` | `float` or `None` | Search radius for candidate vertices; defaults to 15% of mesh height |

**Returns:** `tuple[list[int], float]` — `([idx1, idx2], mean_distance)`, or `(None, max_allowed_dist)` if no suitable pair is found.

---

### Static utilities

---

**`apply_bone_roll_strategy(bone, roll_strategy, roll_reference_z=None)`**

Apply a named roll-alignment strategy to an edit bone in place.

| Argument | Type | Description |
|----------|------|-------------|
| `bone` | `bpy.types.EditBone` | The edit bone to adjust |
| `roll_strategy` | `str` | One of `ALIGN_Z_WORLD_Z`, `ALIGN_X_WORLD_X`, `ALIGN_Z_REFERENCE_Z` |
| `roll_reference_z` | list of 3 floats or `None` | Reference Z vector for `ALIGN_Z_REFERENCE_Z` |

**Returns:** `None`

---

**`get_bone_end_strategy(bone, is_tail)`**

Read the head or tail strategy from a bone's custom properties.

| Argument | Type | Description |
|----------|------|-------------|
| `bone` | `bpy.types.Bone` or `bpy.types.EditBone` | The bone to read from |
| `is_tail` | `bool` | `True` to read the tail strategy, `False` for the head |

**Returns:** `tuple[dict | None, bool]` — `(strategy_dict, is_locked)`. `strategy_dict` is `None` if no strategy is stored.

---

**`assign_bone_end_strategy(bone, info, is_tail, *, force=False, lock=None)`**

Write a head or tail strategy dict to a bone's custom properties.

| Argument | Type | Description |
|----------|------|-------------|
| `bone` | `bpy.types.Bone` or `bpy.types.EditBone` | The bone to write to |
| `info` | `dict` | Strategy dict to store |
| `is_tail` | `bool` | `True` to write the tail strategy, `False` for the head |
| `force` | `bool` | Override the lock flag if set |
| `lock` | `bool` or `None` | Optionally set the lock flag alongside the strategy |

**Returns:** `None`

---

**`get_armature_constraint_vertex_index(con)`**

Extract the vertex index encoded in an `ARMATURE` constraint name using the `VERTEX:<n>` naming convention.

| Argument | Type | Description |
|----------|------|-------------|
| `con` | `bpy.types.ArmatureConstraint` | The constraint whose name is parsed |

**Returns:** `int` or `None` — the vertex index, or `None` if the name does not match the convention.

---

**`ensure_armature_constraint_vertex_index(con, vertex)`**

Update (or prepend) the vertex index in an `ARMATURE` constraint name.

| Argument | Type | Description |
|----------|------|-------------|
| `con` | `bpy.types.ArmatureConstraint` | The constraint to update |
| `vertex` | `int` | The vertex index to encode in the constraint name |

**Returns:** `None`

---

## Examples

**Create an armature from a JSON rig file:**

```python
from mpfb.entities.rig import Rig

rig = Rig.from_json_file_and_basemesh("/path/to/rig.json", basemesh_object)
armature = rig.create_armature_and_fit_to_basemesh()
```

**Extract the current armature state to a dict:**

```python
from mpfb.entities.rig import Rig
import bpy, json

rig = Rig.from_given_basemesh_and_armature(basemesh, bpy.context.active_object)
print(json.dumps(rig.rig_header, indent=2))
```
