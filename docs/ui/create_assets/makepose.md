# Create Assets — MakePose

**Source:** `src/mpfb/ui/create_assets/makepose/`

**Parent panel:** `MPFB_PT_Create_Panel` ("Create assets")

## Overview

MakePose is the tool for saving the current pose of a skeleton armature to a file that can be reloaded later via the Apply Assets panel. Two types of output are supported:

- **Pose files** — a snapshot of the bone rotations (and optionally translations) at a single point in time, saved in MPFB's `.mhpose` format.
- **Animation files** — a full keyframe animation exported from the NLA or action editor, saved in a format compatible with MPFB's animation system.

The panel is only drawn when the active object is a Skeleton (i.e. an armature that MPFB recognises as a character's rig). This is enforced via a `poll()` check that inspects the object type property.

## Panel

### MPFB_PT_MakePose_Panel ("MakePose")

| Attribute | Value |
|---|---|
| `bl_label` | "MakePose" |
| `bl_category` | `RIGCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Create_Panel` |
| `bl_options` | `DEFAULT_CLOSED` |
| Base class | `Abstract_Panel` |

The panel draws four collapsible boxes:

- **General settings** — controls which categories of bone transform are included in the output (`roottrans`, `iktrans`, `fktrans`, `overwrite`).
- **Save pose** — name field and pose type selector, plus the "Save pose" button.
- **Save animation** — "Save animation" button (saves the current action/NLA).
- **Load animation** — "Load animation" button (imports a previously saved animation back onto the skeleton).

## Operators

### MPFB_OT_SavePoseOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.save_pose` |
| `bl_label` | "Save pose" |

Captures the current pose of the active skeleton and writes it to a `.mhpose` file. The file name is taken from the `name` property. The `roottrans`, `iktrans`, and `fktrans` properties determine whether root bone translations, IK bone translations, and FK bone translations respectively are included in the saved data. If `overwrite` is false and a file with the same name already exists, the operation is aborted.

---

### MPFB_OT_SaveAnimationOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.save_animation` |
| `bl_label` | "Save animation" |

Exports the keyframe animation from the active skeleton's current action to an animation file. Opens a file browser for choosing the output path.

---

### MPFB_OT_LoadAnimationOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_animation` |
| `bl_label` | "Load animation" |

Imports a previously exported animation file back onto the active skeleton. Opens a file browser for selecting the file.

## Properties

MakePose uses `MakePoseProperties`, a `SceneConfigSet` loaded from the JSON files in `makepose/objectproperties/` (despite the directory name, these are scene-level properties rather than per-object properties). No JSON properties prefix is used.

| Property | Type | Description |
|---|---|---|
| `name` | string | File name (without extension) to use when saving a pose. |
| `pose_type` | enum | Whether to save a full-body pose or a partial pose (affecting only specific bone groups). |
| `roottrans` | boolean | Include root bone location translations in the saved pose. |
| `iktrans` | boolean | Include IK bone location translations in the saved pose. |
| `fktrans` | boolean | Include FK bone location translations in the saved pose. |
| `overwrite` | boolean | If false, refuse to overwrite an existing file with the same name. |

## Related

- [Apply Assets — applypose](../apply_assets/applypose.md) — load a saved pose back onto a character
- [Rigging](../rigging/index.md) — add and configure a skeleton before posing
