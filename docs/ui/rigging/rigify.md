# Rigging — "Convert to rigify"

**Source:** `src/mpfb/ui/rigging/rigify/`

**Parent panel:** `MPFB_PT_Rig_Panel` ("Rigging")

## Overview

The "Convert to rigify" panel converts a Game Engine rig that is already attached to a character into a Rigify rig. This is an alternative to the two-step "Add Rigify Rig → Generate" workflow in the [Add rig](addrig.md) panel. Use this panel when you already have a character with a Game Engine rig and want to upgrade it to Rigify without removing and re-adding the rig.

The panel only appears when the active object is a skeleton. The operator validates that the rig is of the Game Engine type (by checking for the `ball_r` bone) before proceeding. Attempting to convert a different rig type will produce an error.

Requires the Rigify addon to be enabled in Blender.

## Panel

### MPFB_PT_Rigify_Panel ("Convert to rigify")

| Attribute | Value |
|---|---|
| `bl_label` | "Convert to rigify" |
| `bl_category` | `RIGCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Rig_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Poll | Active object must be a skeleton (`ObjectService.object_is_skeleton()`) |
| Properties prefix | `"RF_"` |

Draws: `name`, `produce`, `keep_meta` properties and the **Rigify** (Convert) button.

## Operators

### MPFB_OT_Convert_To_Rigify_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.convert_to_rigify` |
| `bl_label` | "Rigify" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `RIG_ACTIVE` |

Converts the active Game Engine rig to Rigify. Steps:

1. Applies the rig's location transform (clears the location offset).
2. Creates a `RigifyHelpers` instance from `src/mpfb/entities/rigging/rigifyhelpers.py`.
3. Calls `convert_to_rigify()`, which restructures the bone hierarchy to match Rigify's expectations and sets up the metarig markup data.
4. If `produce` is `True`, immediately runs Rigify's generate step to produce the final rig (equivalent to pressing Generate manually in Rigify's UI).
5. If `keep_meta` is `False` and production ran, deletes the intermediate metarig.
6. Applies the optional `name` to the generated rig if provided.

## Properties

### Scene properties (from JSON, prefix `"RF_"`)

| Property | Type | Default | Description |
|---|---|---|---|
| `name` | string | `""` | Name for the generated rig. If empty, the name configured in the metarig's Object Data Properties (Advanced Options → Rig Name) is used. |
| `produce` | boolean | `true` | Immediately run the Rigify "generate" step after conversion, producing the final rig in one action. If disabled, the result is a Rigify metarig that still needs to be generated manually. |
| `keep_meta` | boolean | `false` | Keep the intermediate Rigify metarig in the scene after generating the final rig. Useful if you need to make adjustments and regenerate. |

## Related

- [addrig.md](addrig.md) — the alternative Rigify workflow (add metarig + generate)
- [RigifyHelpers](../../entities/rigging/rigifyhelpers.md) — the entity class that implements the conversion logic
