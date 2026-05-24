# Operations — "Rig operations"

**Source:** `src/mpfb/ui/operations/rigops/`

**Parent panel:** `MPFB_PT_Operations_Panel` ("Operations")

## Overview

The "Rig operations" panel hosts rig-level operations. Currently the only entry is the legacy "convert to rigify" workflow, which converts a Game Engine rig that is already attached to a character into a Rigify rig.

**This workflow is discouraged for new characters.** Use the modern "Add rigify metarig → Generate" flow on the [Rigging](../rigging/index.md) panel instead. The convert workflow is retained because it is still the only viable Rigify path for characters that were imported from MakeHuman — those characters arrive with a Game Engine rig.

The panel is `DEFAULT_CLOSED` so that the discouraged workflow is not visually prominent. It only draws controls when the active object is a skeleton and the Rigify addon is enabled. The operator validates that the rig is of the Game Engine type (by checking for the `ball_r` bone) before proceeding; attempting to convert a different rig type produces an error.

## Panel

### MPFB_PT_Rig_Operations_Panel ("Rig operations")

| Attribute | Value |
|---|---|
| `bl_label` | "Rig operations" |
| `bl_category` | `OPERATIONSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Operations_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Poll | Active object must be a skeleton (`ObjectService.object_is_skeleton()`) |
| Properties prefix | `"RF_"` |

Draws: a short in-panel note clarifying the MakeHuman-imported-only use case, the `name`, `produce`, `meta_rig_action` properties and the **Rigify** (Convert) button.

The `RF_*` prefix on the scene properties is preserved unchanged from the prior location of this panel under `src/mpfb/ui/rigging/rigify/`, so saved scenes continue to work.

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
2. Creates a `RigifyHelpers` instance from `src/mpfb/entities/rigging/rigifyhelpers/rigifyhelpers.py`.
3. Calls `convert_to_rigify()`, which restructures the bone hierarchy to match Rigify's expectations and sets up the metarig markup data.
4. If `produce` is `True`, immediately runs Rigify's generate step to produce the final rig (equivalent to pressing Generate manually in Rigify's UI).
5. Applies the chosen `meta_rig_action` to the intermediate metarig: `keep` leaves it visible, `hide` (default) sets `hide_viewport` and `hide_render`, `delete` removes it. Only relevant when `produce` ran.
6. Applies the optional `name` to the generated rig if provided.

The `bl_idname` (`mpfb.convert_to_rigify`) is preserved from the prior location of this operator under `src/mpfb/ui/rigging/rigify/`, so keymaps and scripts continue to work.

## Properties

### Scene properties (from JSON, prefix `"RF_"`)

| Property | Type | Default | Description |
|---|---|---|---|
| `name` | string | `""` | Name for the generated rig. If empty, the name configured in the metarig's Object Data Properties (Advanced Options → Rig Name) is used. |
| `produce` | boolean | `true` | Immediately run the Rigify "generate" step after conversion, producing the final rig in one action. If disabled, the result is a Rigify metarig that still needs to be generated manually. |
| `meta_rig_action` | enum | `"hide"` | Label "Meta-rig:". What to do with the intermediate Rigify metarig after generation. Options: `keep` (visible in the scene), `hide` (recommended default — `hide_viewport` and `hide_render`, but the metarig stays in the scene so it can be re-generated in place), `delete` (remove it entirely). |

## Related

- [rigifyrig.md](../rigging/rigifyrig.md) — the modern Rigify workflow (add metarig + generate)
- [RigifyHelpers](../../entities/rigging/rigifyhelpers.md) — the entity class that implements the conversion logic
