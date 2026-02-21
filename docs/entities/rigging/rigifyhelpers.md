# RigifyHelpers / GameEngineRigifyHelpers

## Overview

`RigifyHelpers` converts an MPFB rig to a Rigify metarig by configuring `rigify_type` and `rigify_parameters` on each pose bone, then optionally generating the final production rig. 

**Note that this is the old and stupid way of doing things: to first create a GameEngine rig and then convert it. There is no reason to use this for any other rigify-related workflow.**

The `convert_to_rigify` method is the main entry point; it calls internal setup methods for spine, arms, legs, shoulders, head, and fingers in sequence.

Use `get_instance` to obtain a concrete implementation rather than instantiating `RigifyHelpers` directly. Currently the only concrete subclass is `GameEngineRigifyHelpers`.

**Blender 4.0+ bone-collection migration:** Two static methods handle the upgrade from the integer-layer-based Rigify system used in Blender 3.x to the named-collection system introduced in Blender 4.0:

- `upgrade_rigify_layer_refs` — migrates `*_layers` integer-list parameters in a rig JSON definition to `*_coll_refs` collection-name lists.
- `upgrade_rigify_ui_layers` — upgrades a Rigify UI data dict from the `rigify_layers` format to the `collections` dict format used in Blender 4.0+.

Both methods are called automatically by `Rig._upgrade_definition` when loading a version-100 rig file.

**Post-generation adjustment:** When `produce=True`, `convert_to_rigify` calls `adjust_children_for_rigify` after Rigify generation. This static method finds all child rigs and meshes of the metarig and updates their constraint targets and vertex group names to reference the generated rig instead.

`GameEngineRigifyHelpers` provides the bone-name lists for the game-engine-style MPFB rig. Bone names use underscore suffixes (`_l` / `_r`).

Private methods (prefixed `_`) handle spine, arm, leg, shoulder, head, and finger setup calls, plus the `use_connect` helper. They are not part of the public API.

## Source

- `src/mpfb/entities/rigging/rigifyhelpers/rigifyhelpers.py`
- `src/mpfb/entities/rigging/rigifyhelpers/gameenginerigifyhelpers.py`

## Dependencies

- **Blender:** `bpy`
- **MPFB services:** `LogService`, `RigService`, `ObjectService`, `SystemService`

## Attributes (`RigifyHelpers`)

| Attribute | Type | Description |
|-----------|------|-------------|
| `settings` | `dict` | Configuration dict passed at construction |
| `produce` | `bool` | Whether to call `bpy.ops.pose.rigify_generate` after metarig setup |
| `keep_meta` | `bool` | Whether to keep the metarig object after the generated rig is produced |

## Public API — `RigifyHelpers`

---

**`__init__(settings)`**

Initialise the helper with a configuration dict, extracting `produce` and `keep_meta` flags.

| Argument | Type | Description |
|----------|------|-------------|
| `settings` | `dict` | May include `produce` (bool), `keep_meta` (bool), and `name` (str for the output rig name) |

**Returns:** `RigifyHelpers` instance.

---

**`convert_to_rigify(armature_object)`**

Configure all Rigify bone types on the metarig, then optionally generate the production rig and adjust all child rigs and meshes.

| Argument | Type | Description |
|----------|------|-------------|
| `armature_object` | `bpy.types.Object` | The MPFB armature to convert; must be the active object |

**Returns:** `None`

---

**`get_instance(settings, rigtype="Default")`** *(static)*

Factory method returning a concrete `RigifyHelpers` implementation. Always returns a `GameEngineRigifyHelpers` instance.

| Argument | Type | Description |
|----------|------|-------------|
| `settings` | `dict` | Configuration dict |
| `rigtype` | `str` | Ignored; only one concrete class exists |

**Returns:** `RigifyHelpers` (always `GameEngineRigifyHelpers`).

---

**`adjust_children_for_rigify(rigify_object, armature_object)`** *(static)*

Update all child rigs and meshes of `armature_object` to reference `rigify_object` (the generated rig) instead of the original metarig.

| Argument | Type | Description |
|----------|------|-------------|
| `rigify_object` | `bpy.types.Object` | The newly generated Rigify armature |
| `armature_object` | `bpy.types.Object` | The original metarig being replaced |

**Returns:** `None`

---

**`adjust_skeleton_for_rigify(child_rig, rigify_object, old_armature)`** *(static)*

Update constraint targets on a child rig, remapping bone subtargets from metarig names to their `ORG-` (or `DEF-` for vertex-bound) equivalents in the generated rig.

| Argument | Type | Description |
|----------|------|-------------|
| `child_rig` | `bpy.types.Object` | The subrig to update |
| `rigify_object` | `bpy.types.Object` | The generated Rigify armature |
| `old_armature` | `bpy.types.Object` | The metarig being replaced |

**Returns:** `None`

---

**`adjust_mesh_for_rigify(child_mesh, rigify_object, old_armature)`** *(static)*

Rename vertex groups on a mesh from plain bone names to their `DEF-` equivalents and update the armature modifier to point to the generated rig.

| Argument | Type | Description |
|----------|------|-------------|
| `child_mesh` | `bpy.types.Object` | The mesh object to update |
| `rigify_object` | `bpy.types.Object` | The generated Rigify armature |
| `old_armature` | `bpy.types.Object` | The metarig being replaced |

**Returns:** `None`

---

**`load_rigify_ui(armature_object, rigify_ui)`** *(static)*

Restore Rigify UI colour sets and bone-collection visibility/row state from a saved dict (as produced by `get_rigify_ui`).

| Argument | Type | Description |
|----------|------|-------------|
| `armature_object` | `bpy.types.Object` | The armature to update; must be the active object |
| `rigify_ui` | `dict` | Rigify UI state dict with keys `rigify_colors_lock`, `selection_colors`, `colors`, `collections` |

**Returns:** `None`

---

**`get_rigify_ui(armature_object)`** *(static)*

Extract the current Rigify UI state (colour sets and bone-collection settings) from an armature for serialisation into the rig JSON header.

| Argument | Type | Description |
|----------|------|-------------|
| `armature_object` | `bpy.types.Object` | The armature to read from |

**Returns:** `dict` or `None` — the Rigify UI state dict, or `None` if Rigify is not enabled or the armature has no Rigify UI data.

---

**`upgrade_rigify_layer_refs(rigify, coll_names, coll_used)`** *(static)*

Migrate rig JSON from old integer `*_layers` parameters to named `*_coll_refs` collection references in-place.

| Argument | Type | Description |
|----------|------|-------------|
| `rigify` | `dict` | A bone's rigify dict (with optional `rigify_parameters` and `rigify_type`) |
| `coll_names` | `list[str]` | Ordered list of collection names (index = layer index) |
| `coll_used` | `set[int]` | Set accumulating layer indices that are referenced |

**Returns:** `None`

---

**`upgrade_rigify_ui_layers(rigify_ui, coll_names, coll_used)`** *(static)*

Upgrade a Rigify UI data dict from the old `rigify_layers` list format to the Blender 4.0+ `collections` dict format in-place.

| Argument | Type | Description |
|----------|------|-------------|
| `rigify_ui` | `dict` | Rigify UI dict containing `rigify_layers` |
| `coll_names` | `list[str]` | Ordered list of collection names to populate |
| `coll_used` | `set[int]` | Set accumulating layer indices that are referenced |

**Returns:** `None`

---

### Abstract methods (must be overridden by subclasses)

| Method | Description |
|--------|-------------|
| `get_foot_name(left_side=True)` | Name of the foot bone for the given side |
| `get_list_of_spine_bones()` | Ordered list of spine bone names (root → top) |
| `get_list_of_arm_bones(left_side=True)` | Ordered list of arm bone names for Rigify `limbs.arm` |
| `get_list_of_leg_bones(left_side=True)` | Ordered list of leg bone names for Rigify `limbs.leg` |
| `get_list_of_shoulder_bones(left_side=True)` | List of shoulder/clavicle bone names |
| `get_list_of_head_bones()` | Ordered list of neck and head bone names |
| `get_list_of_finger_bones(finger_number, left_side=True)` | Ordered list of bone names for one finger |

---

## Public API — `GameEngineRigifyHelpers`

`GameEngineRigifyHelpers` extends `RigifyHelpers` and implements all abstract methods for the game-engine-style MPFB rig. Bone names use `_l` / `_r` suffixes:

| Method | Returns (left side) |
|--------|---------------------|
| `get_foot_name(left_side=True)` | `"foot_l"` |
| `get_list_of_spine_bones()` | `["pelvis", "spine_01", "spine_02", "spine_03"]` |
| `get_list_of_arm_bones(left_side=True)` | `["upperarm_l", "lowerarm_l", "hand_l"]` |
| `get_list_of_leg_bones(left_side=True)` | `["thigh_l", "calf_l", "foot_l", "ball_l"]` |
| `get_list_of_shoulder_bones(left_side=True)` | `["clavicle_l"]` |
| `get_list_of_head_bones()` | `["neck_01", "head"]` |
| `get_list_of_finger_bones(finger_number, left_side=True)` | `["thumb_01_l", "thumb_02_l", "thumb_03_l"]` (example for thumb) |

No new public methods are introduced beyond the abstract method implementations.
