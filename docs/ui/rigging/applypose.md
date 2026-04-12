# Rigging — "Load pose"

**Source:** `src/mpfb/ui/rigging/applypose/`

**Parent panel:** `MPFB_PT_Rig_Panel` ("Rigging")

## Overview

The "Load pose" panel applies a saved pose to the currently active armature. Poses are stored as `.json` files in the user's data directory under `poses/`, organised into sub-directories by rig type and mode.

Two categories of poses are supported:

- **Full poses** — replace the entire current pose of all bones. Applied from the `poses/{rig_type}_{fk|ik}/` directory.
- **Partial poses** — override only a specific subset of bones, layered on top of the existing pose without changing the rest. Applied from `poses/{rig_type}_partial/`.

The dropdown menus only list poses that are compatible with the active rig's type and its current FK/IK mode. This prevents accidentally applying a pose designed for a different rig or a rig in a different mode.

On the first time the panel is drawn, `RigService.ensure_global_poses_are_available()` is called. This copies any system-provided pose files that come with MPFB from the addon's data directory into the user's data directory, making them permanently available even after addon updates.

A third option allows importing a pose from a MakeHuman BVH animation file. This is a destructive operation that changes bone roll angles and should only be used when specifically needed.

The panel only appears when the active object is an armature.

## Panel

### MPFB_PT_ApplyPosePanel ("Load pose")

| Attribute | Value |
|---|---|
| `bl_label` | "Load pose" |
| `bl_category` | `RIGCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Rig_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Poll | Active object must be an armature |
| Properties prefix | `"POSES_"` |

Draws: `available_poses` dropdown → **Load pose** button, then `available_partials` dropdown → **Load partial pose** button, then **Import MH BVH Pose** button.

## Operators

### MPFB_OT_Load_Pose_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_pose` |
| `bl_label` | "Load pose" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `ANY_ARMATURE_OBJECT_ACTIVE` |

Applies the selected full pose to the active armature. Steps:

1. Identifies the rig type using `RigService.identify_rig()`. Rigs with "default" in their name are normalised to just `"default"`.
2. Detects whether the rig is in FK or IK mode by checking whether any bone name ends with `"_ik"`. Sets the directory suffix to `"_fk"` or `"_ik"` accordingly.
3. Constructs the path `poses/{rig_type}_{mode}/{pose_name}.json` inside the user data directory.
4. Loads the JSON file and applies all bone rotations using `RigService.set_pose_from_dict()`.

---

### MPFB_OT_Load_Partial_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_partial` |
| `bl_label` | "Load partial pose" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `ANY_ARMATURE_OBJECT_ACTIVE` |

Same as Load Pose, except:

- Uses the `_partial` directory suffix to look up the pose file.
- Calls `RigService.set_pose_from_dict(..., from_rest_pose=False)`, which applies the saved bone values on top of the current pose rather than from the rest position. Bones not mentioned in the partial pose file are left exactly as they are.

---

### MPFB_OT_Load_MH_BVH_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_mhbvh_pose` |
| `bl_label` | "Import MH BVH Pose" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| File filter | `*.bvh` |
| Poll | `ANY_ARMATURE_OBJECT_ACTIVE` |

Opens a file browser filtered to `.bvh` (BioVision Hierarchy) animation files. After the user selects a file, calls `AnimationService.import_bvh_file_as_pose()` to extract the first frame of the BVH animation and apply it as a static pose to the armature.

**Warning:** This operation changes the bone roll angles of all bones in the rig, making the armature behave differently for subsequent posing and animation. Only use this when you specifically need to bring in a MakeHuman BVH pose and are prepared to deal with the side effects.

## Properties

Both properties are defined directly in `applyposepanel.py` (not in JSON files) because their option lists are populated dynamically by scanning the file system at draw time.

| Property | Type | Description |
|---|---|---|
| `available_poses` | enum (dynamic) | Lists all full pose `.json` files found in `poses/{rig_type}_{fk\|ik}/` in the user data directory. The list is filtered to only show poses that match the active rig's type and mode. Empty if no matching poses are installed. |
| `available_partials` | enum (dynamic) | Lists all partial pose `.json` files found in `poses/{rig_type}_partial/` in the user data directory. Empty if no matching partial poses are installed. |

## Related

- [RigService](../../services/rigservice.md) — provides `identify_rig()`, `set_pose_from_dict()`, and `ensure_global_poses_are_available()`
- [AnimationService](../../services/animationservice.md) — provides `import_bvh_file_as_pose()`
- [Pose file format](../../fileformats/pose.md) — the `.json` format used for stored poses
