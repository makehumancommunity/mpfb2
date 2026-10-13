# RigService

## Overview

RigService provides a comprehensive collection of static methods for working with armatures, rigs, bones, bone constraints, poses, and vertex weights. It is the primary service for all skeletal operations in MPFB, handling everything from rig creation and bone manipulation to weight painting and pose management.

The service supports multiple rig types: the MPFB **default** rig (with and without individual toes), **game engine** rigs, **Rigify** metarigs and generated rigs, **Mixamo**, **CMU Motion Builder**, **OpenPose** rigs, and **custom rigs** saved to the user library. Rig type identification is based on the presence of characteristic bone names, with custom rigs identified via their `"identifying_bones"` list obtained from `AssetService`. Custom rigs are reported with a `"custom."` prefix (e.g., `"custom.my_rig"`). The service provides weight-loading fallback chains so that weights from compatible rig types can be reused.

RigService also manages armature refitting — the process of adjusting bone positions to match a morphed basemesh — provides bone visualization tools for displaying bones as empties, NURBS paths, or UV spheres, and owns the Rigify generation pipeline via `generate_rigify_rig`, which is the single implementation shared by every UI path that turns a Rigify meta rig into a generated control rig. All methods are static; the class should never be instantiated.

Two things are worth knowing before reading the method list.

**The bone lookups are nullable, and most of the service does not check them.** `find_pose_bone_by_name`
and `find_edit_bone_by_name` return `None` for a name the armature does not have, because the blender
collections they read do. Every other method which takes a bone name and then reads something off the
bone does so unguarded, so a name that is not in the armature raises `AttributeError` rather than being
reported. The bone name is a precondition the caller is expected to satisfy; the methods are not defensive
about it, and there is nothing useful most of them could do with a bone that does not exist. The
exceptions are noted per method.

**Three areas do not work as documented below, and are marked where they appear.** Weight symmetrization
is unimplemented and raises on any rig but the default; `get_world_space_location_of_pose_bone` returns
its two entries under each other's key; and the subrig branch of `ensure_armature_modifier` calls an
operator form blender removed. Each is described at the method it affects rather than only here.

## Source

`src/mpfb/services/rigservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.rigservice")` |
| `LocationService` | Resolving paths to pose files, weight files, and rig definitions |
| `SystemService` | Checking for Rigify addon availability |
| `TargetService` | Baking shape keys during rest pose application |
| `ObjectService` | Object activation, selection, children queries, Rigify detection |
| `SkeletonObjectProperties` | Reading/writing skeleton custom properties (extra bones) |
| `Rig` | Rig entity for armature refitting (imported at call time) |
| `GeneralObjectProperties` | Reading UUID properties for subrig refitting (imported at call time) |
| `ClothesService` | Finding clothes asset paths for subrig refitting (imported at call time) |
| `AssetService` | Querying custom rig definitions for identification and refitting (imported at call time) |

## Rig Type Identifiers

The `identify_rig()` method returns one of these string identifiers:

| Type | Description |
|------|-------------|
| `"default"` | MPFB default rig with individual toes |
| `"default_no_toes"` | MPFB default rig without individual toes |
| `"game_engine"` | Game engine rig (UE-style bone names) |
| `"game_engine_with_breast"` | Game engine rig with breast bones |
| `"cmu_mb"` | CMU Motion Builder rig |
| `"mixamo"` | Mixamo rig |
| `"mixamo_unity"` | Mixamo rig with Unity naming and breast bones |
| `"openpose"` | OpenPose rig |
| `"rigify.human"` | Rigify metarig (human, no toes) |
| `"rigify.human_toes"` | Rigify metarig (human, with toes) |
| `"rigify_generated.game_engine"` | Generated Rigify rig from game engine metarig |
| `"rigify_generated.human"` | Generated Rigify rig (human, no toes) |
| `"rigify_generated.human_toes"` | Generated Rigify rig (human, with toes) |
| `"rigify.unknown"` | Rigify metarig of unknown subtype |
| `"rigify_generated.unknown"` | Generated Rigify rig of unknown subtype |
| `"unknown"` | Unrecognized rig type |
| `"custom.<name>"` | A custom rig saved to user data, where `<name>` is the bare filename (e.g., `"custom.my_rig"`) |

## Module-Level Types

| Name | Definition | Notes |
|------|------------|-------|
| `MhwWeights` | `dict[str, Any]` | The MHW weights dictionary, as `get_weights` produces it and `apply_weights` consumes it. The metadata keys — `copyright`, `description`, `license`, `name`, `version` — are written for MakeHuman compatibility and are not read anywhere in MPFB. The only key MPFB reads is `weights`, mapping a vertex group name to a list of `[vertex index, weight]` pairs. An alias rather than a `TypedDict` because a file written by MakeHuman or by an older MPFB need not carry the metadata keys at all, and because the values arrive from `json.load` as `Any`. |
| `PoseInfo` | `dict[str, Any]` | A serialized pose, as `get_pose_as_dict` writes it and `set_pose_from_dict` reads it: `skeleton_type`, `bone_rotations`, `bone_rotation_modes`, `bone_translations`, `has_ik_bones`, `original_spine_length` and `original_shoulder_width`. An alias rather than a `TypedDict` because a pose file written by an older MPFB carries no `bone_rotation_modes` at all — `set_pose_from_dict` infers the mode from the length of the rotation list in that case. |
| `SkeletonBoneInfo` | `dict[str, Any]` | One node of the bone tree inside a `SocketSkeletonInfo`, as the private `_add_bone` consumes it: `name`, `headPos`, `tailPos` and `children`, plus the optional `matrix` and `roll`. A node carrying `matrix` has its `roll` ignored. |
| `RotationMode` | `Literal["QUATERNION", "XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX", "AXIS_ANGLE"]` | The eight values blender's bone rotation mode enum accepts, verified against `PoseBone.bl_rna` on both blender 4.2.1 and 5.1, where the list is identical. Used by `normalize_rotation_mode`. |

Three further shapes crossing this service's signatures are declared in `src/mpfb/types.py`, because they
are shared with the entities layer rather than owned here: `BoneOrientationInfo` and `BoneOrientation`
(what `get_bone_orientation_info_as_dict` returns, which all four rig helper hierarchies store) and
`SocketSkeletonInfo` (what `SocketService.get_skeleton` returns, which `create_rig_from_skeleton_info`
consumes).

## Public API

### Rig Creation and Setup

#### create_rig_from_skeleton_info(name, data, parent=None, scale=0.1)

Create a new armature object from a skeleton information dictionary. The data dictionary must contain a `"bones"` key with hierarchical bone definitions including head/tail positions, optional matrices or roll values, and children. Bones are positioned with Z-up coordinate conversion.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The name for the new armature |
| `data` | `SocketSkeletonInfo` | — | Skeleton info dictionary with bone data. Each entry of its `bones` list is a `SkeletonBoneInfo`. |
| `parent` | `bpy.types.Object \| None` | `None` | Optional parent object. **Currently unusable:** see the note below. |
| `scale` | `float` | `0.1` | Scale factor for bone positions |

**Returns:** `bpy.types.Object` — The created armature object.

> **`parent` does not work.** The argument is handed to `ObjectService.link_blender_object` positionally,
> so it lands in that method's `collection` parameter rather than its `parent` one. A non-`None` value
> therefore raises `AttributeError` inside `ObjectService` (a `bpy.types.Object` has no `objects`
> collection to link into) and the parent is never assigned. Latent: the only caller in the tree —
> `SocketBodyObject`, which parents the body mesh to the returned armature itself — passes `None`
> explicitly, and `link_blender_object` then falls back to the active collection, which is the intended
> behaviour. Pass `None` and parent the result yourself.

---

#### ensure_armature_modifier(obj, armature_object, *, move_to_top=True, subrig=None)

Ensure a mesh object has an armature modifier pointing to the given armature. Creates the modifier if it doesn't exist, or updates the target if it does. Also handles preserve-volume modifiers (using `mhmask-preserve-volume` vertex group) and subrig modifiers (using `mhmask-subrig` vertex group), ensuring correct modifier stacking order.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `obj` | `bpy.types.Object` | — | The mesh object to modify |
| `armature_object` | `bpy.types.Object \| None` | — | The armature to link. A falsy value makes the method retarget the modifiers that already exist and then return without creating any. |
| `move_to_top` | `bool` | `True` | Move the armature modifier to the top of the stack |
| `subrig` | `bpy.types.Object \| None` | `None` | Optional subrig armature for a secondary modifier |

**Returns:** `None`

> **The subrig branch raises.** The loop that moves the newly created `Armature Subrig` modifier up the
> stack calls `bpy.ops.object.modifier_move_up({'object': obj}, modifier=...)`, which is the pre-3.2
> context override form. Blender 4.2 raises `ValueError` and blender 5.x raises `TypeError` for it, so
> the loop cannot complete on any supported version. The two sibling loops above it — for the plain and
> the preserve-volume modifiers — use `bpy.context.temp_override()` and work. The branch is only entered
> when a `subrig` is passed and the mesh does not already carry a `mhmask-subrig` armature modifier, and
> the loop body is only reached when the mesh carries modifiers *after* the armature ones, which an MPFB
> basemesh with a helper mask and a subdivision modifier does.

---

#### ensure_armature_has_bone_shape_objects_as_children(armature_object)

Ensure the armature has hidden empty objects for bone custom shapes (circle, sphere, arrow) as children. Creates any that are missing.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to check |

**Returns:** `None`

---

#### normalize_rotation_mode(armature_object, rotation_mode="XYZ")

Set the rotation mode of all pose bones in the armature to the specified mode.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to normalize |
| `rotation_mode` | `RotationMode` | `"XYZ"` | The rotation mode to set. One of the eight values of blender's rotation mode enum, not an arbitrary string; see Module-Level Types. |

**Returns:** `None`

---

#### ensure_global_poses_are_available()

Copy built-in MPFB pose files (JSON) from the source data directory to the user data directory if they don't already exist. Creates subdirectories as needed.

**Returns:** `None`

---

### Bone Lookup and Activation

#### find_pose_bone_by_name(name, armature_object)

Find a pose bone by name in the armature's pose bone collection.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The bone name to find |
| `armature_object` | `bpy.types.Object` | — | The armature object |

**Returns:** `bpy.types.PoseBone | None` — The pose bone, or `None` if not found. Note that most of the rest of this service calls this method and then reads the result without checking; see the Overview.

---

#### find_edit_bone_by_name(name, armature_object)

Find an edit bone by name. Requires the armature to be in Edit mode.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The bone name to find |
| `armature_object` | `bpy.types.Object` | — | The armature object |

**Returns:** `bpy.types.EditBone | None` — The edit bone, or `None` if not found. Requires the armature to be in Edit mode, since `Armature.edit_bones` is empty otherwise.

---

#### activate_pose_bone_by_name(name, armature_object, also_select_bone=True, also_deselect_all_other_bones=True)

Activate a specific pose bone, making it the active bone in the armature. Optionally selects the bone and deselects all others.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The bone name to activate |
| `armature_object` | `bpy.types.Object` | — | The armature object |
| `also_select_bone` | `bool` | `True` | Also select the bone |
| `also_deselect_all_other_bones` | `bool` | `True` | Deselect all other bones first |

**Returns:** `bpy.types.PoseBone` — The activated pose bone. Raises `AttributeError` for a name the armature does not have, since the lookup is not checked.

> **Selection does not work on blender 5.** This method selects and deselects by writing `pose_bone.bone.select`. Blender moved that flag from `bpy.types.Bone` to `bpy.types.PoseBone` in 5.0, so the write raises `AttributeError` there; it works on 4.2 and 4.3. No code in MPFB calls this method, which is why it has gone unnoticed. The same two lines appear in `set_pose_from_dict`, where they *are* reachable.

---

#### get_world_space_location_of_pose_bone(bone_name, armature_object)

Get the head and tail positions of a pose bone in world space by transforming through the armature's world matrix.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone name |
| `armature_object` | `bpy.types.Object` | — | The armature object |

**Returns:** `dict[str, Vector]` — Two entries, `"head"` and `"tail"`, each a position in world space.

> **The two entries are swapped.** `loc["head"]` holds the transformed *tail* and `loc["tail"]` the
> transformed *head*. The transform itself is correct — `matrix_world @` the bone-local position, which
> is more correct than the two sibling methods below — but the keys are the wrong way round, so a caller
> reading the dict by name gets each bone end's position under the other end's key. The sole caller,
> the OpenPose export operator, does read it by name, so every keypoint it defines as a bone head is
> exported at that bone's tail and vice versa.

---

#### find_pose_bone_tail_world_location(bone_name, armature_object)

Find the world-space location of a pose bone's tail.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone name |
| `armature_object` | `bpy.types.Object` | — | The armature object |

**Returns:** `Vector` — The tail position, computed as `bone.tail + armature_object.location`. Note that this is not a full world-space transform: it adds the armature's translation only, so it is correct only for an armature that is neither rotated nor scaled. `get_world_space_location_of_pose_bone` applies `matrix_world` instead.

---

#### find_pose_bone_head_world_location(bone_name, armature_object)

Find the world-space location of a pose bone's head.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone name |
| `armature_object` | `bpy.types.Object` | — | The armature object |

**Returns:** `Vector` — The head position, computed as `bone.head + armature_object.location`, with the same caveat as the tail method above.

---

### Bone Constraints

#### add_bone_constraint_to_pose_bone(bone_name, armature_object, constraint_name)

Add a constraint of the specified type to a pose bone.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone to constrain |
| `armature_object` | `bpy.types.Object` | — | The armature object |
| `constraint_name` | `str` | — | The constraint type (e.g., `'COPY_ROTATION'`, `'IK'`) |

**Returns:** `bpy.types.Constraint` — The created constraint, as the `bpy.types.Constraint` base class. The parameter is deliberately a plain `str` rather than blender's constraint-type enum, because callers build it from asset data; a value the enum does not contain raises at runtime. Callers which set type-specific settings on the result have to narrow it to the subclass the type string selects, which the rig helpers in `entities/rigging/righelpers` do with a `typing.cast`.

---

#### remove_all_constraints_from_pose_bone(bone_name, armature_object)

Remove all constraints from a pose bone and reset all IK lock and limit flags.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone to clear constraints from |
| `armature_object` | `bpy.types.Object` | — | The armature object |

**Returns:** `None`

---

#### add_copy_rotation_constraint_to_pose_bone(bone_to_restrain_name, bone_to_copy_from_name, armature_object, copy_x=True, copy_y=True, copy_z=True)

Add a Copy Rotation constraint to a pose bone. The constraint copies rotation from another bone in the same armature in local space.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_to_restrain_name` | `str` | — | The bone to add the constraint to |
| `bone_to_copy_from_name` | `str` | — | The bone to copy rotation from |
| `armature_object` | `bpy.types.Object` | — | The armature object |
| `copy_x` | `bool` | `True` | Copy rotation around X axis |
| `copy_y` | `bool` | `True` | Copy rotation around Y axis |
| `copy_z` | `bool` | `True` | Copy rotation around Z axis |

**Returns:** `bpy.types.CopyRotationConstraint` — The created constraint.

---

#### add_rotation_constraint_to_pose_bone(bone_name, armature_object, limit_x=False, limit_y=False, limit_z=False)

Add a Limit Rotation constraint to a pose bone in local space.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone to constrain |
| `armature_object` | `bpy.types.Object` | — | The armature object |
| `limit_x` | `bool` | `False` | Limit rotation around X axis |
| `limit_y` | `bool` | `False` | Limit rotation around Y axis |
| `limit_z` | `bool` | `False` | Limit rotation around Z axis |

**Returns:** `bpy.types.LimitRotationConstraint` — The created constraint.

---

#### add_ik_rotation_lock_to_pose_bone(bone_name, armature_object, lock_x=False, lock_y=False, lock_z=False)

Lock a pose bone's rotation on specified axes during IK solving.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone to lock |
| `armature_object` | `bpy.types.Object` | — | The armature object |
| `lock_x` | `bool` | `False` | Lock X axis rotation |
| `lock_y` | `bool` | `False` | Lock Y axis rotation |
| `lock_z` | `bool` | `False` | Lock Z axis rotation |

**Returns:** `bpy.types.PoseBone` — The modified pose bone. Raises `AttributeError` for a name the armature does not have.

---

#### add_ik_constraint_to_pose_bone(bone_name, armature_object, target, chain_length=2)

Add an Inverse Kinematics constraint to a pose bone. The target can be either an external object or a pose bone within the same armature (in which case the armature becomes the target with the bone as subtarget).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone to constrain |
| `armature_object` | `bpy.types.Object` | — | The armature object |
| `target` | `bpy.types.Object \| bpy.types.PoseBone` | — | The IK target |
| `chain_length` | `int` | `2` | Number of bones in the IK chain |

**Returns:** `bpy.types.KinematicConstraint` — The created IK constraint.

---

#### set_ik_rotation_limits(bone_name, armature_object, axis, min_angle=0, max_angle=0)

Set IK rotation limits for a pose bone on a specified axis. Angles are provided in degrees and converted to radians internally.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone to set limits on |
| `armature_object` | `bpy.types.Object` | — | The armature object |
| `axis` | `str` | — | The axis to limit (`"x"`, `"y"`, or `"z"`) |
| `min_angle` | `float` | `0` | Minimum angle in degrees |
| `max_angle` | `float` | `0` | Maximum angle in degrees |

**Returns:** `None`

An `axis` other than `"x"`, `"y"` or `"z"` matches none of the three branches and is silently ignored.

---

### Bone Orientation and Measurement

#### get_bone_orientation_info_as_dict(armature_object)

Retrieve the orientation information of all bones in an armature, including head/tail positions, matrices, roll, length, and parent names. Collects data from both pose mode and edit mode.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to analyze |

**Returns:** `BoneOrientationInfo` — `{"pose_bones": {name: BoneOrientation}, "edit_bones": {name: BoneOrientation}}`, where a pose entry carries `head`, `tail` and `matrix` and an edit entry additionally carries `roll`, `length` and `parent`. Declared in `src/mpfb/types.py`, since all four rig helper hierarchies store the result. Note that the method changes mode three times — to `POSE`, then `EDIT`, then back to `OBJECT` — because the two halves are only readable in their own mode.

---

#### set_bone_orientation_from_info_in_dict(armature_object, new_bone_orientation)

Set bone orientations from a dictionary (as returned by `get_bone_orientation_info_as_dict`). Processes bones in parent-to-child order to maintain correct hierarchical positioning.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to update |
| `new_bone_orientation` | `BoneOrientationInfo` | — | Orientation data dictionary |

**Returns:** `None`

---

#### find_leg_length(armature_object)

Calculate the total length of the right leg bones (`upperleg01.R`, `upperleg02.R`, `lowerleg01.R`, `lowerleg02.R`). Only implemented for the default rig type.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to measure |

**Returns:** `float` — Total leg bone length.

**Raises:** `ValueError` if not a default rig or if bones are missing.

---

#### find_arm_length(armature_object)

Calculate the total length of the right arm bones (`upperarm01.R`, `upperarm02.R`, `lowerarm01.R`, `lowerarm02.R`). Only implemented for the default rig type.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to measure |

**Returns:** `float` — Total arm bone length.

**Raises:** `ValueError` if not a default rig or if bones are missing.

---

### Weight Management

#### get_weights(armature_objects, basemesh, exclude_weights_below=0.0001, all_groups=False, all_bones=False, all_masks=True)

Create an MHW-compatible weights dictionary from the current vertex group weights on a basemesh. The dictionary includes metadata fields (`copyright`, `description`, `license`, `name`, `version`) for compatibility with the MakeHuman weight format.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_objects` | `list[bpy.types.Object] \| bpy.types.Object` | — | The armature(s) to use for bone matching. A single armature is wrapped in a list internally. |
| `basemesh` | `bpy.types.Object` | — | The mesh to extract weights from |
| `exclude_weights_below` | `float` | `0.0001` | Minimum weight to include |
| `all_groups` | `bool` | `False` | Include all vertex groups, not just bone-matching ones |
| `all_bones` | `bool` | `False` | Include all deform bones even without vertex groups |
| `all_masks` | `bool` | `True` | Include `mhmask-*` vertex groups |

**Returns:** `MhwWeights` — MHW-format weights dictionary; see Module-Level Types.

---

#### load_weights(armature_objects, basemesh, mhw_filename, *, all=False, replace=False)

Load vertex weights from a JSON file and apply them to the basemesh.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_objects` | `list[bpy.types.Object] \| bpy.types.Object` | — | The armature(s) for bone matching |
| `basemesh` | `bpy.types.Object` | — | The mesh to apply weights to |
| `mhw_filename` | `str` | — | Path to the MHW JSON file |
| `all` | `bool` | `False` | Load all groups even without matching bones |
| `replace` | `bool` | `False` | Replace existing weights entirely |

**Returns:** `None`

`all` and `replace` are keyword-only.

---

#### apply_weights(armature_objects, basemesh, mhw_dict, *, all=False, replace=False)

Apply weights from a dictionary to the basemesh. Maps weight group names to bones with automatic `DEF-` prefix fallback and common toe matching. Groups are processed in bone topology order.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_objects` | `list[bpy.types.Object] \| bpy.types.Object` | — | The armature(s) for bone matching |
| `basemesh` | `bpy.types.Object` | — | The mesh to apply weights to |
| `mhw_dict` | `MhwWeights` | — | MHW-format weights dictionary; see Module-Level Types |
| `all` | `bool` | `False` | Load all groups even without matching bones |
| `replace` | `bool` | `False` | Replace existing weights entirely |

**Returns:** `None`

`all` and `replace` are keyword-only.

---

#### mirror_bone_weights_to_other_side_bone(armature_object, source_bone_name, target_bone_name)

**Not implemented.** The body logs the bone pair and returns; no weight is read or written and
`armature_object` is not touched at all. The name and the signature describe the intent, not the
behaviour. The only caller is `symmetrize_all_bone_weights`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | Accepted and unused |
| `source_bone_name` | `str` | — | Name of the source bone; logged only |
| `target_bone_name` | `str` | — | Name of the target bone; logged only |

**Returns:** `None`

---

#### mirror_bone_weights_inside_center_bone(armature_object, bone_name, left_to_right=False)

**Not implemented**, in the same way as the method above: the body logs its arguments and returns. Intended
to mirror weights within a center bone, a bone that spans both sides of the mesh.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | Accepted and unused |
| `bone_name` | `str` | — | Name of the center bone; logged only |
| `left_to_right` | `bool` | `False` | Logged only |

**Returns:** `None`

---

#### symmetrize_all_bone_weights(armature_object, left_to_right=False, rig_type=None)

Walk the bones of the armature, classify each as a source side, a destination side or a center bone by its
suffix (`.L` / `.R`), and hand each one to the matching mirror method.

> **This changes no weights.** Both mirror methods it delegates to are unimplemented (see the two entries
> above), so the walk has no effect. The two UI operators that call it — "Copy left to right" and "Copy
> right to left" on the MakeWeight panel — nonetheless report `Weight symmetrized`.
>
> **It also raises for any rig but the default.** The suffix table is keyed by rig type and carries a
> single `"default"` row. A falsy or `"unknown"` rig type is rewritten to `"default"`; every other value
> `identify_rig` can return reaches the lookup unchanged and raises `KeyError` before a single bone is
> visited. `"default_no_toes"` is the reachable case that matters, being the MPFB default rig without
> individual toes.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to symmetrize |
| `left_to_right` | `bool` | `False` | If `True`, mirror from left to right |
| `rig_type` | `str \| None` | `None` | Rig type for suffix detection, auto-detected with `identify_rig` if `None` |

**Returns:** `None`

**Raises:** `KeyError` if the resolved rig type has no row in the suffix table, which is every type other than `"default"`.

---

### Extra Bones / Rigify

#### set_extra_bones(armature_object, extra_bones)

Store a list of extra bone names as a custom property on the armature. Used to track bones that will be generated by Rigify but don't exist in the metarig.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to set the property on |
| `extra_bones` | `list[str] \| None` | — | List of bone names, or `None` (or an empty list) to remove the property |

**Returns:** None

---

#### get_extra_bones(armature_object)

Retrieve the list of extra bone names stored on the armature's custom properties.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to query |

**Returns:** `list[str]` — List of extra bone names (empty list if not set).

---

#### get_deform_group_bones(armature_object)

Get all bones that should have vertex groups: bones marked `use_deform` plus any extra bones from `find_extra_bones`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to query |

**Returns:** `list[str]` — List of deform group bone names.

---

#### find_extra_bones(armature_object)

Identify deform bones that will be generated by Rigify but are not present in the metarig. Compares the metarig's deform bones against the generated rig's `DEF-` prefixed bones. Falls back to stored extra bones if no generated rig exists.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The metarig to analyze |

**Returns:** `list[str]` — Sorted list of extra bone names, empty if there are none. **Never `None`**, contrary to what this doc and the method's own annotation previously said: the branch which finds no generated rig falls back to `get_extra_bones`, which answers an empty list.

---

#### generate_rigify_rig(meta_rig, *, name="", meta_rig_action="hide")

Run Rigify generation on a meta rig and return the generated control rig. This helper is the single implementation shared by the UI operator `mpfb.generate_rigify_rig`, the auto-generate path in `mpfb.add_rigify_rig`, and the post-deserialize auto-generate path in `mpfb.human_from_presets`.

The caller is responsible for verifying that `meta_rig` is a Rigify meta rig (typically via `RigService.identify_rig()`, which should return a value starting with `"rigify."`) and that the Rigify addon is enabled (typically via `SystemService.check_for_rigify()`). As a final gate the helper additionally calls `rigify.utils.rig.is_valid_metarig`; if Rigify itself considers the meta rig invalid the helper returns `None` without running `pose.rigify_generate`, so the caller can emit a `{'WARNING'}` of its own. The import of `is_valid_metarig` is guarded so MPFB still loads cleanly when Rigify is not enabled.

The helper handles renaming a `.rig`-suffixed meta rig back to `.metarig`, applying the optional `name` as `rigify_rig_basename`, the legacy issue-#17 basename workaround, selecting the meta rig and switching to object mode, running `pose.rigify_upgrade_face` when available, calling `pose.rigify_generate` (which will update the existing rig in place when `meta_rig.data.rigify_target_rig` is already set), re-parenting the resulting rig to match the meta rig's parent, calling `RigifyHelpers.adjust_children_for_rigify`, copying `object_type` onto the rigify rig via `GeneralObjectProperties`, applying the requested `meta_rig_action`, and leaving the generated rig active in object mode.

`meta_rig_action` controls what happens to the meta rig after generation:

| Value      | Behaviour |
|------------|-----------|
| `"keep"`   | Leave the meta rig untouched. |
| `"hide"`   | (default) Keep the meta rig in the scene but set `hide_viewport = True` and `hide_render = True`. Preserves Rigify's in-place re-generation target while keeping the outliner uncluttered. |
| `"delete"` | Remove the meta rig from `bpy.data.objects`. In-place re-generation is no longer possible after this. |

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `meta_rig` | `bpy.types.Object` | — | The Rigify meta rig armature |
| `name` | `str` | `""` | Optional basename for the generated rig |
| `meta_rig_action` | `str` | `"hide"` | What to do with the meta rig after generation: `"keep"`, `"hide"`, or `"delete"`. Unknown values fall back to `"hide"` with a warning. |

**Returns:** `bpy.types.Object | None` — The generated (or in-place updated) rigify rig, or `None` if `is_valid_metarig` rejected the meta rig.

---

### Rig Identification

#### identify_rig(armature_object)

Identify the rig type by checking for characteristic bone names. Uses a prioritized matching table where later matches override earlier ones. Falls back to Rigify detection and Mixamo name pattern matching. If the rig still cannot be identified as a built-in type, it queries `AssetService.get_custom_rigs()` and checks whether all bones listed in each custom rig's `"identifying_bones"` are present in the armature. The first matching custom rig wins and is returned as `"custom.<name>"`. Built-in rigs always take precedence over custom rigs.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to identify |

**Returns:** `str` — One of the rig type identifiers (see Rig Type Identifiers section), including `"custom.<name>"` for user-defined rigs.

---

#### infer_metarig_type_from_generated(rigify_object)

Infer the corresponding rigify meta-rig type for a generated rigify rig. This is the inverse of the `rigify_generated.*` rows in `identify_rig` and is used when a generated rigify rig must be serialized back to a meta-rig type string — for example when saving a character whose only remaining rig is a generated one. The caller is responsible for verifying that the input is in fact a generated rigify rig, typically via `ObjectService.object_is_generated_rigify_rig`.

| Bones present on the generated rig                | Returns               |
|---------------------------------------------------|-----------------------|
| `ORG-brow.T.R.002` AND `ORG-toe2-1.L`             | `"rigify.human_toes"` |
| `ORG-brow.T.R.002` (no toes marker)               | `"rigify.human"`      |
| anything else                                     | `None`                |

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `rigify_object` | `bpy.types.Object` | — | The generated rigify rig armature |

**Returns:** `str | None` — A `"rigify.<variant>"` meta-rig type string, or `None` if no signature matches. Callers should fall back to a sensible default and emit a warning when `None` is returned.

---

#### get_rig_weight_fallbacks(rig_type)

Get an ordered list of rig types to try when loading weights. Provides fallbacks so that compatible weight files can be used across similar rig types (e.g., toes vs. no-toes variants).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `rig_type` | `str` | — | The primary rig type |

**Returns:** `list[str]` — Ordered list of rig types to try.

---

### Pose Management

#### set_pose_from_dict(armature_object, pose, from_rest_pose=True)

Apply a pose from a dictionary of bone rotations and translations. For the default rig, translations are scaled based on the ratio between the current spine/shoulder dimensions and the original dimensions stored in the pose. If `from_rest_pose` is `True`, all bones are cleared to rest pose first.

Rotation handling is mode-aware: each bone's `rotation_mode` is set from `pose["bone_rotation_modes"][name]` (or inferred from the array length when the legacy format omits the modes map — 4 floats → `"QUATERNION"`, 3 floats → `"XYZ"`), then the rotation is written to the matching attribute (`rotation_quaternion`, `rotation_axis_angle`, or `rotation_euler`). This is what makes the function work on generated Rigify rigs, where many control bones default to quaternion mode.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to pose |
| `pose` | `PoseInfo` | — | Pose dictionary with `bone_rotations`, `bone_translations`, `skeleton_type` and optionally `bone_rotation_modes`; see Module-Level Types |
| `from_rest_pose` | `bool` | `True` | Clear to rest pose before applying |

**Returns:** `None`

> **The `from_rest_pose=False` path does not work on blender 5.** That path selects the bones the pose
> mentions by writing `pose_bone.bone.select`, a flag blender moved from `bpy.types.Bone` to
> `bpy.types.PoseBone` in 5.0, so it raises `AttributeError` there; it works on 4.2 and 4.3. The default
> path selects with `bpy.ops.pose.select_all` instead and is unaffected. `mpfb.load_partial_pose` is the
> operator that takes the broken path.

Note that the spine and shoulder measurements are read from four hard-coded bone names — `spine05`,
`spine01`, `shoulder01.L` and `shoulder01.R` — whenever `pose["skeleton_type"]` contains `"default"`, and
the lookups are not checked. Those names come from the *saved* pose while the bones are looked up on the
*current* armature, so applying a default-rig pose to an armature without them raises `AttributeError`.
The two UI operators cannot reach that, because they choose the pose directory from `identify_rig` on the
armature they are about to pose.

---

#### get_pose_as_dict(armature_object, root_bone_translation=True, ik_bone_translation=True, fk_bone_translation=False, onlyselected=False)

Serialize the current pose to a dictionary. Includes bone rotations, selected bone translations, rig type, and spine/shoulder measurements for proportional retargeting. Each bone's rotation is captured in its native representation (3-element euler, 4-element quaternion, or 4-element axis-angle), and the per-bone rotation mode is recorded under `bone_rotation_modes`. Bones whose rotation is effectively identity are omitted.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to read |
| `root_bone_translation` | `bool` | `True` | Include root bone translation |
| `ik_bone_translation` | `bool` | `True` | Include IK bone translations |
| `fk_bone_translation` | `bool` | `False` | Include FK bone translations |
| `onlyselected` | `bool` | `False` | Only include selected bones |

**Returns:** `PoseInfo` — Pose dictionary; see Module-Level Types. The same four hard-coded bone names as `set_pose_from_dict` are read, unchecked, when `identify_rig` reports a default rig — which is what guarantees they exist on this path.

---

#### apply_pose_as_rest_pose(armature_object)

Apply the current pose as the new rest pose. For each child mesh: bakes shape keys on basemeshes, applies armature modifiers, applies the pose as rest pose, then recreates armature modifiers.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to apply |

**Returns:** `None`

---

#### copy_pose(from_armature, to_armature, only_rotation=True)

Copy the pose from one armature to another by matching bone names. By default only copies rotations, but can also copy translations and scales.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `from_armature` | `bpy.types.Object` | — | Source armature |
| `to_armature` | `bpy.types.Object` | — | Target armature |
| `only_rotation` | `bool` | `True` | If `True`, only copy rotations; if `False`, also copy translations and scales |

**Returns:** `None`

Bones present in the source but not the target are silently skipped, and vice versa; matching is by name only.

---

### Rig Refitting

#### refit_existing_armature(armature_object, basemesh)

Refit an armature to a new basemesh shape. For Rigify generated rigs, automatically finds and refits the metarig instead, then regenerates. For custom rigs (identified by `"custom."` prefix), looks up the rig JSON file via `AssetService.get_custom_rigs()` and calls the internal refit helper directly. Uses rig JSON definition files to determine bone-to-vertex mappings.

Raises `ValueError("Cannot refit a generated rigify rig")` when the input is a generated rigify rig and no meta rig is present in the scene; reconstructing the meta rig in that case is more invasive than is justified, so the user-visible remedy is to enable "Keep meta rig" before generating. Callers — for instance `HumanService.refit`, which accepts an `operator` keyword for exactly this purpose — should catch the `ValueError` and surface it as an operator-level `{'ERROR'}` report rather than letting it propagate.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to refit |
| `basemesh` | `bpy.types.Object` | — | The target basemesh |

**Returns:** `None`

**Raises:** `ValueError` if the rig type cannot be identified, if it's a generated Rigify rig (should refit the metarig instead), or if the custom rig is no longer present in user data.

---

#### refit_existing_subrig(armature_object, parent_rig)

Refit a subrig (secondary armature for clothes/accessories) to match its parent rig. Finds the associated asset mesh and uses the `.mpfbskel` file alongside the asset for bone positioning.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The subrig armature object to refit |
| `parent_rig` | `Rig` | — | The parent rig to fit to. **An `entities.rig.Rig` instance, not an armature object** — this doc previously said `bpy.types.Object`, which was wrong. It is handed straight to `Rig.from_json_file_and_basemesh` as the `parent` of the subrig definition being loaded, and that constructor reads `.armature_object` and `.rig_definition` off it. `HumanService.refit`, the only caller, builds one with `Rig.from_given_basemesh_and_armature`. |

**Returns:** `None`

**Raises:** `ValueError` if the asset mesh or asset file cannot be found.

---

### Bone Visualization

#### display_pose_bone_as_empty(armature_object, bone_name, empty_type="SPHERE", scale=1.0)

Set a pose bone's custom shape to an empty object. Ensures the required bone shape empty objects (circle, sphere, arrow) exist as children of the armature.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature |
| `bone_name` | `str` | — | The bone to display |
| `empty_type` | `str` | `"SPHERE"` | Type of empty (`"SPHERE"`, `"CIRCLE"`, `"SINGLE_ARROW"`) |
| `scale` | `float` | `1.0` | Scale factor for the custom shape |

**Returns:** `None`

The scale is applied through whichever of `custom_shape_scale` and `custom_shape_scale_xyz` the pose bone has, tested with `hasattr`. Only the latter exists on blender 4.2 and later, so the first branch is dead on every supported version and is kept for older ones. If no matching bone shape empty is found, the method logs a warning and leaves the bone alone.

---

#### add_path_object_to_bone(armature_object, bone_name, bevel_depth=0.015)

Create a NURBS path object parented to a bone. The path runs from the bone's head to its tail with a bevel for visual thickness. Useful for bone visualization and debugging.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature |
| `bone_name` | `str` | — | The bone to attach the path to |
| `bevel_depth` | `float` | `0.015` | Bevel depth for the NURBS path |

**Returns:** `bpy.types.Object` — The created NURBS path object.

**Raises:** `ValueError` if the bone is not found.

---

#### add_uv_sphere_object_to_bone(armature_object, bone_name, sphere_scale=0.01, tail_rather_than_head=False)

Create a UV sphere object parented to a bone at its head or tail position. Useful for visualizing joint positions.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature |
| `bone_name` | `str` | — | The bone to attach the sphere to |
| `sphere_scale` | `float` | `0.01` | Scale of the UV sphere |
| `tail_rather_than_head` | `bool` | `False` | Place at tail instead of head |

**Returns:** `bpy.types.Object` — The created sphere object.

**Raises:** `ValueError` if the bone is not found.

---

## Examples

### Creating and Setting Up a Rig

```python
from mpfb.services.rigservice import RigService
from mpfb.services.objectservice import ObjectService

# Create a rig from skeleton data. Leave parent at None: passing anything else raises,
# for the reason given under create_rig_from_skeleton_info above.
armature = RigService.create_rig_from_skeleton_info(
    "MyRig", skeleton_data, parent=None, scale=0.1
)

# Parent the basemesh to the rig yourself
ObjectService.link_blender_object(basemesh, parent=armature)

# Add armature modifier to the basemesh
RigService.ensure_armature_modifier(basemesh, armature)

# Identify the rig type
rig_type = RigService.identify_rig(armature)
print(f"Rig type: {rig_type}")
```

### Working with Poses

```python
from mpfb.services.rigservice import RigService
import json

# Ensure built-in poses are available
RigService.ensure_global_poses_are_available()

# Save the current pose
pose = RigService.get_pose_as_dict(armature)
with open("/path/to/pose.json", "w") as f:
    json.dump(pose, f)

# Load and apply a pose. Leave from_rest_pose at its default: the partial path
# selects bones through Bone.select, which blender 5 removed.
with open("/path/to/pose.json", "r") as f:
    saved_pose = json.load(f)
RigService.set_pose_from_dict(armature, saved_pose)

# Copy pose between armatures
RigService.copy_pose(source_armature, target_armature, only_rotation=True)
```

### Managing Weights

```python
from mpfb.services.rigservice import RigService

# Extract weights from current setup. Accepts one armature or a list of them.
weights = RigService.get_weights(armature, basemesh)

# Save weights to file
import json
with open("/path/to/weights.json", "w") as f:
    json.dump(weights, f)

# Load weights from file. all and replace are keyword-only.
RigService.load_weights(armature, basemesh, "/path/to/weights.json", all=True)

# Get the weight loading fallback chain for a rig type
fallbacks = RigService.get_rig_weight_fallbacks("default_no_toes")
# Returns: ["default_no_toes", "default"]
```
