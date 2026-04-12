# Rigging — "Add walk cycle" (deprecated)

**Source:** `src/mpfb/ui/rigging/addcycle/`

**Parent panel:** `MPFB_PT_Rig_Panel` ("Rigging")

## Overview

> **This section is deprecated.** The walk cycle functionality has been superseded by the Mixamo workflow. The panel is retained in the codebase for backwards compatibility but displays only a deprecation notice — no functional controls are shown.

The original intent of this section was to load a pre-authored walk cycle animation from a JSON file and apply it to the active character's rig. It was never reliable enough for practical use, and the Mixamo rig and retargeting approach provides a much better solution for character animation.

## Panel

### MPFB_PT_Add_Cycle_Panel ("Add walk cycle")

| Attribute | Value |
|---|---|
| `bl_label` | "Add walk cycle" |
| `bl_category` | `MODELCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Rig_Panel` |
| Base class | `Abstract_Panel` |
| Poll | Visible when the active object has a skeleton amongst its nearest relatives |

The `draw()` method displays a single box containing the message:

> DEPRECATED in favor of mixamo functionality (and it never worked particularly well in the first place)

No controls or operator buttons are drawn.

## Operators

### MPFB_OT_Load_Walk_Cycle_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_walk_cycle` |
| `bl_label` | "Load walk cycle" |
| `bl_options` | `{'REGISTER'}` |
| Poll | `ANY_ARMATURE_OBJECT_ACTIVE` |

This operator is **not exposed in the panel UI**. It exists as a code remnant. Conceptually, it would load a walk cycle animation from a JSON file in `mpfb/data/walkcycles/`, validate that all bones referenced in the file exist in the active rig, and apply the animation using `AnimationService.walk_cycle_from_dict()`.
