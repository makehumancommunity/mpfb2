# Operations — "Poses"

**Source:** `src/mpfb/ui/operations/poseops/`

**Parent panel:** `MPFB_PT_Operations_Panel` ("Operations")

## Overview

The "Poses" panel provides two operators that work with poses on MPFB skeleton objects. A "pose" in Blender is the set of bone rotations and positions stored on an armature when it is in pose mode; the "rest pose" is the neutral, unposed position that the mesh is bound to.

- **Apply as rest pose** permanently bakes the current pose into the rest pose. This is useful when you want the character to always start in a non-T-pose (e.g. a relaxed A-pose) without relying on a pose being applied at render time. It is a destructive, one-way operation.
- **Copy pose** copies the current pose from one rig to one or more other rigs of the same type. This is useful for transferring poses between characters or for quickly mirroring a pose library entry onto a different character.

The panel is only shown when the active object is a skeleton (armature). The `objtype` check specifically requires the type to be `"Skeleton"` as assigned by MPFB.

## Panel

### MPFB_PT_PoseopsPanel ("Poses")

| Attribute | Value |
|---|---|
| `bl_label` | "Poses" |
| `bl_category` | `OPERATIONSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Operations_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"POP_"` |

The panel draws two collapsible boxes:

- **Apply pose** — the **Apply as rest pose** button.
- **Copy pose** — the `only_rotation` toggle and the **Copy pose** button.

## Operators

### MPFB_OT_Apply_Pose_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.apply_pose` |
| `bl_label` | "Apply as rest pose" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `RIG_ACTIVE` |

Applies the current pose as the new rest pose by calling `RigService.apply_pose_as_rest_pose(obj)`. After this operation, the armature's bones are repositioned so the current pose becomes the new "zero" position. All mesh objects parented to the armature have their bind pose updated accordingly.

**Warning:** This operation internally calls the shape-key baking process so that all morph targets are collapsed into the final mesh before the rest pose is changed. Afterward, you will no longer be able to adjust morphing targets. Only use this when character customisation is complete.

---

### MPFB_OT_Copy_Pose_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.copy_pose` |
| `bl_label` | "Copy pose" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `RIG_ACTIVE` |

Copies the current pose from the active armature to all other selected armatures. The workflow is: first select all target rigs, then Shift-click the source rig to make it active, then click **Copy pose**. Multiple targets can be updated in a single operation.

Before copying, the operator verifies that all selected objects are armatures and that the source and each target are the same rig type (as returned by `RigService.identify_rig()`). If a type mismatch is found, the operation is aborted with an error.

The `only_rotation` property controls whether only bone rotations are copied (suitable for rigs at different positions in the scene) or both rotation and location (suitable for rigs at the same position).

Pose copying is performed by `RigService.copy_pose(source, target, only_rotation)` for each target armature.

## Scene Properties

Properties are stored with the `POP_` prefix on the scene object.

| Property | Type | Default | Description |
|---|---|---|---|
| `only_rotation` | boolean | — | When copying a pose, copy only bone rotation values and leave bone locations unchanged |

## Related

- [Operations index](index.md)
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md)
