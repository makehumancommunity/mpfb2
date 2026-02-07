# RigService

## Overview

RigService provides a comprehensive collection of static methods for working with armatures, rigs, bones, bone constraints, poses, and vertex weights. It is the primary service for all skeletal operations in MPFB, handling everything from rig creation and bone manipulation to weight painting and pose management.

The service supports multiple rig types: the MPFB **default** rig (with and without individual toes), **game engine** rigs, **Rigify** metarigs and generated rigs, **Mixamo**, **CMU Motion Builder**, and **OpenPose** rigs. Rig type identification is based on the presence of characteristic bone names, and the service provides weight-loading fallback chains so that weights from compatible rig types can be reused.

RigService also manages armature refitting — the process of adjusting bone positions to match a morphed basemesh — and provides bone visualization tools for displaying bones as empties, NURBS paths, or UV spheres. All methods are static; the class should never be instantiated.

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

## Public API

### Rig Creation and Setup

#### create_rig_from_skeleton_info(name, data, parent=None, scale=0.1)

Create a new armature object from a skeleton information dictionary. The data dictionary must contain a `"bones"` key with hierarchical bone definitions including head/tail positions, optional matrices or roll values, and children. Bones are positioned with Z-up coordinate conversion.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The name for the new armature |
| `data` | `dict` | — | Skeleton info dictionary with bone data |
| `parent` | `bpy.types.Object` | `None` | Optional parent object |
| `scale` | `float` | `0.1` | Scale factor for bone positions |

**Returns:** `bpy.types.Object` — The created armature object.

---

#### ensure_armature_modifier(obj, armature_object, *, move_to_top=True, subrig=None)

Ensure a mesh object has an armature modifier pointing to the given armature. Creates the modifier if it doesn't exist, or updates the target if it does. Also handles preserve-volume modifiers (using `mhmask-preserve-volume` vertex group) and subrig modifiers (using `mhmask-subrig` vertex group), ensuring correct modifier stacking order.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `obj` | `bpy.types.Object` | — | The mesh object to modify |
| `armature_object` | `bpy.types.Object` | — | The armature to link |
| `move_to_top` | `bool` | `True` | Move the armature modifier to the top of the stack |
| `subrig` | `bpy.types.Object` | `None` | Optional subrig armature for a secondary modifier |

**Returns:** None

---

#### ensure_armature_has_bone_shape_objects_as_children(armature_object)

Ensure the armature has hidden empty objects for bone custom shapes (circle, sphere, arrow) as children. Creates any that are missing.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to check |

**Returns:** None

---

#### normalize_rotation_mode(armature_object, rotation_mode="XYZ")

Set the rotation mode of all pose bones in the armature to the specified mode.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to normalize |
| `rotation_mode` | `str` | `"XYZ"` | The Euler rotation order to set |

**Returns:** None

---

#### ensure_global_poses_are_available()

Copy built-in MPFB pose files (JSON) from the source data directory to the user data directory if they don't already exist. Creates subdirectories as needed.

**Returns:** None

---

### Bone Lookup and Activation

#### find_pose_bone_by_name(name, armature_object)

Find a pose bone by name in the armature's pose bone collection.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The bone name to find |
| `armature_object` | `bpy.types.Object` | — | The armature object |

**Returns:** `bpy.types.PoseBone` or `None` — The pose bone, or `None` if not found.

---

#### find_edit_bone_by_name(name, armature_object)

Find an edit bone by name. Requires the armature to be in Edit mode.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The bone name to find |
| `armature_object` | `bpy.types.Object` | — | The armature object |

**Returns:** `bpy.types.EditBone` or `None` — The edit bone, or `None` if not found.

---

#### activate_pose_bone_by_name(name, armature_object, also_select_bone=True, also_deselect_all_other_bones=True)

Activate a specific pose bone, making it the active bone in the armature. Optionally selects the bone and deselects all others.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The bone name to activate |
| `armature_object` | `bpy.types.Object` | — | The armature object |
| `also_select_bone` | `bool` | `True` | Also select the bone |
| `also_deselect_all_other_bones` | `bool` | `True` | Deselect all other bones first |

**Returns:** `bpy.types.PoseBone` — The activated pose bone.

---

#### get_world_space_location_of_pose_bone(bone_name, armature_object)

Get the head and tail positions of a pose bone in world space by transforming through the armature's world matrix.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone name |
| `armature_object` | `bpy.types.Object` | — | The armature object |

**Returns:** `dict` — `{"head": Vector, "tail": Vector}` in world space.

---

#### find_pose_bone_tail_world_location(bone_name, armature_object)

Find the world-space location of a pose bone's tail.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone name |
| `armature_object` | `bpy.types.Object` | — | The armature object |

**Returns:** `Vector` — The tail position in world space.

---

#### find_pose_bone_head_world_location(bone_name, armature_object)

Find the world-space location of a pose bone's head.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone name |
| `armature_object` | `bpy.types.Object` | — | The armature object |

**Returns:** `Vector` — The head position in world space.

---

### Bone Constraints

#### add_bone_constraint_to_pose_bone(bone_name, armature_object, constraint_name)

Add a constraint of the specified type to a pose bone.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone to constrain |
| `armature_object` | `bpy.types.Object` | — | The armature object |
| `constraint_name` | `str` | — | The constraint type (e.g., `'COPY_ROTATION'`, `'IK'`) |

**Returns:** `bpy.types.Constraint` — The created constraint.

---

#### remove_all_constraints_from_pose_bone(bone_name, armature_object)

Remove all constraints from a pose bone and reset all IK lock and limit flags.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone to clear constraints from |
| `armature_object` | `bpy.types.Object` | — | The armature object |

**Returns:** None

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

**Returns:** `bpy.types.Constraint` — The created constraint.

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

**Returns:** `bpy.types.Constraint` — The created constraint.

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

**Returns:** `bpy.types.PoseBone` — The modified pose bone.

---

#### add_ik_constraint_to_pose_bone(bone_name, armature_object, target, chain_length=2)

Add an Inverse Kinematics constraint to a pose bone. The target can be either an external object or a pose bone within the same armature (in which case the armature becomes the target with the bone as subtarget).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bone_name` | `str` | — | The bone to constrain |
| `armature_object` | `bpy.types.Object` | — | The armature object |
| `target` | `bpy.types.Object` or `bpy.types.PoseBone` | — | The IK target |
| `chain_length` | `int` | `2` | Number of bones in the IK chain |

**Returns:** `bpy.types.Constraint` — The created IK constraint.

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

**Returns:** None

---

### Bone Orientation and Measurement

#### get_bone_orientation_info_as_dict(armature_object)

Retrieve the orientation information of all bones in an armature, including head/tail positions, matrices, roll, length, and parent names. Collects data from both pose mode and edit mode.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to analyze |

**Returns:** `dict` — `{"pose_bones": {name: {head, tail, matrix}}, "edit_bones": {name: {head, tail, matrix, roll, length, parent}}}`.

---

#### set_bone_orientation_from_info_in_dict(armature_object, new_bone_orientation)

Set bone orientations from a dictionary (as returned by `get_bone_orientation_info_as_dict`). Processes bones in parent-to-child order to maintain correct hierarchical positioning.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to update |
| `new_bone_orientation` | `dict` | — | Orientation data dictionary |

**Returns:** None

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
| `armature_objects` | `bpy.types.Object` or `list` | — | The armature(s) to use for bone matching |
| `basemesh` | `bpy.types.Object` | — | The mesh to extract weights from |
| `exclude_weights_below` | `float` | `0.0001` | Minimum weight to include |
| `all_groups` | `bool` | `False` | Include all vertex groups, not just bone-matching ones |
| `all_bones` | `bool` | `False` | Include all deform bones even without vertex groups |
| `all_masks` | `bool` | `True` | Include `mhmask-*` vertex groups |

**Returns:** `dict` — MHW-format weights dictionary with `"weights"` key.

---

#### load_weights(armature_objects, basemesh, mhw_filename, *, all=False, replace=False)

Load vertex weights from a JSON file and apply them to the basemesh.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_objects` | `bpy.types.Object` or `list` | — | The armature(s) for bone matching |
| `basemesh` | `bpy.types.Object` | — | The mesh to apply weights to |
| `mhw_filename` | `str` | — | Path to the MHW JSON file |
| `all` | `bool` | `False` | Load all groups even without matching bones |
| `replace` | `bool` | `False` | Replace existing weights entirely |

**Returns:** None

---

#### apply_weights(armature_objects, basemesh, mhw_dict, *, all=False, replace=False)

Apply weights from a dictionary to the basemesh. Maps weight group names to bones with automatic `DEF-` prefix fallback and common toe matching. Groups are processed in bone topology order.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_objects` | `list[bpy.types.Object]` or `bpy.types.Object` | — | The armature(s) for bone matching |
| `basemesh` | `bpy.types.Object` | — | The mesh to apply weights to |
| `mhw_dict` | `dict` | — | MHW-format weights dictionary |
| `all` | `bool` | `False` | Load all groups even without matching bones |
| `replace` | `bool` | `False` | Replace existing weights entirely |

**Returns:** None

---

#### mirror_bone_weights_to_other_side_bone(armature_object, source_bone_name, target_bone_name)

Mirror vertex weights from a source side bone to the corresponding target side bone.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature containing the bones |
| `source_bone_name` | `str` | — | Name of the source bone |
| `target_bone_name` | `str` | — | Name of the target bone |

**Returns:** None

---

#### mirror_bone_weights_inside_center_bone(armature_object, bone_name, left_to_right=False)

Mirror vertex weights within a center bone (a bone that spans both sides of the mesh).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature containing the bone |
| `bone_name` | `str` | — | Name of the center bone |
| `left_to_right` | `bool` | `False` | If `True`, mirror from left to right |

**Returns:** None

---

#### symmetrize_all_bone_weights(armature_object, left_to_right=False, rig_type=None)

Symmetrize all bone weights across the rig. Identifies side bones by their suffix (e.g., `.L` / `.R`) and mirrors weights from the source side to the destination side. Center bones are mirrored internally.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to symmetrize |
| `left_to_right` | `bool` | `False` | If `True`, mirror from left to right |
| `rig_type` | `str` | `None` | Rig type for suffix detection (auto-detected if `None`) |

**Returns:** None

---

### Extra Bones / Rigify

#### set_extra_bones(armature_object, extra_bones)

Store a list of extra bone names as a custom property on the armature. Used to track bones that will be generated by Rigify but don't exist in the metarig.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to set the property on |
| `extra_bones` | `list[str]` or `None` | — | List of bone names, or `None` to remove the property |

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

**Returns:** `list[str]` or `None` — Sorted list of extra bone names, or `None`.

---

### Rig Identification

#### identify_rig(armature_object)

Identify the rig type by checking for characteristic bone names. Uses a prioritized matching table where later matches override earlier ones. Falls back to Rigify detection and Mixamo name pattern matching.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to identify |

**Returns:** `str` — One of the rig type identifiers (see Constants section).

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

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to pose |
| `pose` | `dict` | — | Pose dictionary with `bone_rotations`, `bone_translations`, and `skeleton_type` |
| `from_rest_pose` | `bool` | `True` | Clear to rest pose before applying |

**Returns:** None

---

#### get_pose_as_dict(armature_object, root_bone_translation=True, ik_bone_translation=True, fk_bone_translation=False, onlyselected=False)

Serialize the current pose to a dictionary. Includes bone rotations (Euler), selected bone translations, rig type, and spine/shoulder measurements for proportional retargeting.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to read |
| `root_bone_translation` | `bool` | `True` | Include root bone translation |
| `ik_bone_translation` | `bool` | `True` | Include IK bone translations |
| `fk_bone_translation` | `bool` | `False` | Include FK bone translations |
| `onlyselected` | `bool` | `False` | Only include selected bones |

**Returns:** `dict` — Pose dictionary.

---

#### apply_pose_as_rest_pose(armature_object)

Apply the current pose as the new rest pose. For each child mesh: bakes shape keys on basemeshes, applies armature modifiers, applies the pose as rest pose, then recreates armature modifiers.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to apply |

**Returns:** None

---

#### copy_pose(from_armature, to_armature, only_rotation=True)

Copy the pose from one armature to another by matching bone names. By default only copies rotations, but can also copy translations and scales.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `from_armature` | `bpy.types.Object` | — | Source armature |
| `to_armature` | `bpy.types.Object` | — | Target armature |
| `only_rotation` | `bool` | `True` | If `True`, only copy rotations; if `False`, also copy translations and scales |

**Returns:** None

---

### Rig Refitting

#### refit_existing_armature(armature_object, basemesh)

Refit an armature to a new basemesh shape. For Rigify generated rigs, automatically finds and refits the metarig instead, then regenerates. Uses rig JSON definition files to determine bone-to-vertex mappings.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to refit |
| `basemesh` | `bpy.types.Object` | — | The target basemesh |

**Returns:** None

**Raises:** `ValueError` if the rig type cannot be identified or if it's a generated Rigify rig (should refit the metarig instead).

---

#### refit_existing_subrig(armature_object, parent_rig)

Refit a subrig (secondary armature for clothes/accessories) to match its parent rig. Finds the associated asset mesh and uses the `.mpfbskel` file alongside the asset for bone positioning.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The subrig to refit |
| `parent_rig` | `bpy.types.Object` | — | The parent rig to fit to |

**Returns:** None

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

**Returns:** None

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

# Create a rig from skeleton data
armature = RigService.create_rig_from_skeleton_info(
    "MyRig", skeleton_data, parent=basemesh, scale=0.1
)

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

# Load and apply a pose
with open("/path/to/pose.json", "r") as f:
    saved_pose = json.load(f)
RigService.set_pose_from_dict(armature, saved_pose)

# Copy pose between armatures
RigService.copy_pose(source_armature, target_armature, only_rotation=True)
```

### Managing Weights

```python
from mpfb.services.rigservice import RigService

# Extract weights from current setup
weights = RigService.get_weights(armature, basemesh)

# Save weights to file
import json
with open("/path/to/weights.json", "w") as f:
    json.dump(weights, f)

# Load weights from file
RigService.load_weights(armature, basemesh, "/path/to/weights.json")

# Get the weight loading fallback chain for a rig type
fallbacks = RigService.get_rig_weight_fallbacks("default_no_toes")
# Returns: ["default_no_toes", "default"]
```
