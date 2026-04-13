# Operations — "Export copy"

**Source:** `src/mpfb/ui/operations/exportops/`

**Parent panel:** `MPFB_PT_Operations_Panel` ("Operations")

## Overview

The "Export copy" panel creates a deep copy of a fully assembled MPFB character for use in other applications. An "export copy" is an independent duplicate of the entire character hierarchy — including the basemesh, any rig, and all attached clothing and body parts — with a configurable set of cleanup operations applied to it. The original character is left untouched.

Typical reasons to create an export copy include:

- **Baking shape keys** so the mesh is at its final morph positions without any shape key data blocks.
- **Loading facial animation shape keys** (visemes, ARKit face units) that are not part of the standard MPFB character but are needed for real-time or game-engine use.
- **Cleaning up modifiers** — baking or removing mask and subdivision modifiers that are not meaningful outside of Blender.
- **Removing helper geometry** that is only needed for MPFB's internal clothing workflow.

The panel is shown whenever a basemesh can be found among the active object's relatives (poll strategy: `BASEMESH_AMONGST_RELATIVES`). This means you can trigger it from the rig, from a clothing piece, or from the basemesh itself.

## Panel

### MPFB_PT_ExportOpsPanel ("Export copy")

| Attribute | Value |
|---|---|
| `bl_label` | "Export copy" |
| `bl_category` | `OPERATIONSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Operations_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"EXPO_"` |

The panel draws three collapsible boxes:

- **Basemesh** — `mask_modifiers`, `subdiv_modifiers`, `bake_shapekeys`, `delete_helpers`, `remove_basemesh` settings.
- **Visemes and faceunits** — `visemes_meta`, `visemes_microsoft`, `faceunits_arkit`, `interpolate` toggles.
- **Create copy** — `suffix` and `collection` settings, plus the **Create export copy** button.

## Operators

### MPFB_OT_Create_Export_Copy_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.export_copy` |
| `bl_label` | "Create export copy" |
| `bl_options` | `{'REGISTER'}` |
| Poll | `BASEMESH_AMONGST_RELATIVES` |

Creates a deep copy of the character using `ExportService.create_character_copy()`. The copy is placed into an "export copy" collection if `collection` is enabled, or into the same collection as the original basemesh if not. The copy's objects are named with the `suffix` string appended.

After creating the copy, the operator applies the configured cleanup operations in the following order:

1. **Bake shape keys** (if `bake_shapekeys`) — calls `TargetService.bake_targets()` on the new basemesh, collapsing all morph targets into the final geometry.
2. **Load facial shape keys** (if any of `visemes_meta`, `visemes_microsoft`, or `faceunits_arkit`) — calls `FaceService.load_targets()` to add the requested shape key packs. This loads them with zero weight so they can be driven by game-engine blend shapes or facial animation controllers.
3. **Interpolate targets** (if `interpolate`) — calls `FaceService.interpolate_targets()` to generate intermediate shape keys between the loaded facial shapes.
4. **Handle modifiers** — calls `ExportService.bake_modifiers_remove_helpers()` which:
   - Bakes mask modifiers if `mask_modifiers == "BAKE"`.
   - Bakes subdivision modifiers if `subdiv_modifiers == "BAKE"`.
   - Deletes helper geometry if `delete_helpers` is enabled.
5. **Remove mask modifiers** (if `mask_modifiers == "REMOVE"`) — removes all MASK-type modifiers from the new basemesh.
6. **Remove subdivision modifiers** (if `subdiv_modifiers == "REMOVE"`) — removes all SUBSURF-type modifiers.
7. **Remove basemesh** (if `remove_basemesh`) — deletes the basemesh from the copy, leaving only the rig and clothing. Useful when the workflow only needs the clothing meshes.

## Scene Properties

Properties are stored with the `EXPO_` prefix on the scene object.

| Property | Type | Default | Description |
|---|---|---|---|
| `mask_modifiers` | enum | `"KEEP"` | How to handle mask modifiers on the copy: `KEEP` (leave them), `REMOVE` (delete them), `BAKE` (apply them to the mesh) |
| `subdiv_modifiers` | enum | `"KEEP"` | How to handle subdivision modifiers: `KEEP`, `REMOVE`, or `BAKE` |
| `bake_shapekeys` | boolean | — | Bake all morph targets into the final geometry of the copy |
| `delete_helpers` | boolean | — | Remove helper geometry (HelperGeometry and JointCubes vertex groups) from the copy |
| `remove_basemesh` | boolean | — | Delete the basemesh from the copy after all other operations are complete |
| `visemes_meta` | boolean | — | Load Meta (visemes02) facial shape keys onto the copy's basemesh |
| `visemes_microsoft` | boolean | — | Load Microsoft/SSML (visemes01) facial shape keys onto the copy's basemesh |
| `faceunits_arkit` | boolean | — | Load ARKit (faceunits01) facial shape keys onto the copy's basemesh |
| `interpolate` | boolean | — | Generate interpolated intermediate shapes between the loaded facial shape keys |
| `suffix` | string | — | Text appended to object names in the copy (e.g. `"_export"`) |
| `collection` | boolean | — | Place the copy in a dedicated "export copy" collection rather than the original's collection |

## Related

- [Operations index](index.md)
- [Face operations](faceops.md) — loads the same facial shape key packs interactively
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md)
