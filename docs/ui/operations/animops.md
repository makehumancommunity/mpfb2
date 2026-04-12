# Operations — "Animation"

**Source:** `src/mpfb/ui/operations/animops/`

**Parent panel:** `MPFB_PT_Operations_Panel` ("Operations")

## Overview

The "Animation" panel provides tools for working with animation on MPFB characters, with a focus on Mixamo integration. Mixamo is an Adobe online service that offers automatic character rigging and a library of pre-made animations. The typical workflow for using Mixamo animations with an MPFB character involves:

1. Creating a reduced copy of the character (using **Mixamo reduced doll**) and uploading it to Mixamo.
2. Downloading the Mixamo animation on a Mixamo rig.
3. Importing the Mixamo rig and animation into Blender alongside the MPFB character.
4. Mapping the Mixamo animation onto the MPFB rig (using **Snap to mixamo**).
5. Optionally making the animation loop (using **Make cyclic**) or repeating it over time (using **Repeat animation**).

The panel is only drawn when an active object exists. The Mixamo mapping and cyclic/repeat operators additionally require the active object to be an armature.

## Panel

### MPFB_PT_AnimopsPanel ("Animation")

| Attribute | Value |
|---|---|
| `bl_label` | "Animation" |
| `bl_category` | `OPERATIONSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Operations_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"ANIO_"` |

The panel draws four collapsible boxes when the relevant conditions are met:

- **Reduced doll** — always shown when an active object exists. Contains the `call_fbx` toggle and the **Mixamo reduced doll** button.
- **Map mixamo** — shown when the active object is an armature and exactly two armatures are selected. Displays the auto-detected source and destination rig names and the **Snap to mixamo** button.
- **Make cyclic** — shown when the active object is an armature. Contains the `shiftroot` toggle and, if enabled, the `rootbone` field, plus the **Make cyclic** button.
- **Repeat animation** — shown when the active object is an armature. Contains `iterations`, `offset`, `skipfirst`, `shiftroot`, and (if `shiftroot` is enabled) `firstframe` and `rootbone` fields, plus the **Repeat animation** button.

## Operators

### MPFB_OT_Reduced_Doll_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.reduced_doll` |
| `bl_label` | "Mixamo reduced doll" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `ANY_MAKEHUMAN_OBJECT_ACTIVE` |

Creates a stripped-down copy of the character suitable for upload to Mixamo. The character must have a basemesh parented to a rig.

The operator duplicates the rig and basemesh, removes all modifiers from the basemesh copy except the armature modifier (which is relinked to the new skeleton), and then calls `mpfb.delete_helpers` and `mpfb.bake_shapekeys` on the copy to produce a clean, game-ready mesh. The resulting pair of objects is named `<original>_reduced` and `<original>_body_reduced`.

If the `call_fbx` scene property is enabled, the Blender FBX export dialog is opened automatically after the copy is created, with only the new objects selected. This lets you export and upload to Mixamo in one step.

A warning is issued if the rig is not a Mixamo-type rig, since Mixamo expects its own skeleton format.

---

### MPFB_OT_Map_Mixamo_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.map_mixamo` |
| `bl_label` | "Snap to mixamo" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Exactly two armatures must be selected |

Maps a Mixamo animation from a source rig onto a destination rig by adding bone constraints. Both selected armatures must be Mixamo rigs (their bone names must contain a `mixamorig:` prefix).

The operator automatically determines which rig is the source (the one without an MPFB basemesh among its relatives) and which is the destination (the one with a basemesh). If both or neither has a basemesh, the active object is treated as the destination.

For each bone in the destination rig, a `COPY_ROTATION` constraint is added pointing to the matching bone in the source rig. A `COPY_LOCATION` constraint is additionally added to the hip bone so the root motion is also transferred. If the rigs do not have identical bone sets, a warning is issued but the operation proceeds for the bones that do match.

---

### MPFB_OT_Make_Cyclic_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.make_cyclic` |
| `bl_label` | "Make cyclic" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `ANY_ARMATURE_OBJECT_ACTIVE` |

Makes the current animation loop seamlessly by adding an F-Curve Cycles modifier to every F-curve on the armature. This calls `AnimationService.make_cyclic()`.

If `shiftroot` is enabled and a `rootbone` name is specified, the root bone's translation will be adjusted when the cycle loops so the character continues to move forward rather than snapping back to the origin. This is useful for walk cycles where the hips translate over time.

**Warning:** This operator fails silently if any F-curves already have modifiers applied to them. Always apply this to a clean animation without pre-existing F-curve modifiers.

---

### MPFB_OT_Repeat_Animation_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.repeat_animation` |
| `bl_label` | "Repeat animation" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `ANY_ARMATURE_OBJECT_ACTIVE` |

**Experimental.** Duplicates the entire animation `iterations` times, appending each copy at the end of the previous one and optionally offsetting the root bone's position so the character continues moving in the same direction.

The operator calculates the total displacement of the root bone (identified by the `rootbone` property, typically `mixamorig:Hips`) over the animation and shifts each repeated copy by a corresponding multiple of that distance. The `offset` property adds an extra frame gap between repetitions, and `skipfirst` skips the first keyframe of each repeated copy (useful when the first and last frames are identical in a looping animation).

If a simple seamless loop is all you need, **Make cyclic** (above) is the better choice. **Repeat animation** is intended for cases where you want a finite, editable timeline with explicit repeated copies.

## Scene Properties

Properties are stored with the `ANIO_` prefix on the scene object.

| Property | Type | Default | Description |
|---|---|---|---|
| `call_fbx` | boolean | — | Open the FBX export dialog after creating the reduced doll |
| `shiftroot` | boolean | — | Shift root bone position when cycling or repeating |
| `rootbone` | string | — | Name of the root/hip bone to use for root motion calculations |
| `iterations` | int | 10 | Number of times to repeat the animation |
| `offset` | int | — | Extra frame gap between repeated copies |
| `skipfirst` | boolean | — | Skip the first keyframe of each repeated copy |
| `firstframe` | int | — | First frame index to use when repeating with root shift |

## Related

- [Operations index](index.md)
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md)
