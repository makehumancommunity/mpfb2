# Create Assets — MakeRig

**Source:** `src/mpfb/ui/create_assets/makerig/`

**Parent panel:** `MPFB_PT_Create_Panel` ("Create assets")

## Overview

MakeRig is the tool for developing and authoring custom rig definition files. While the [Rigging section](../rigging/index.md) covers *applying* pre-built rigs to characters, MakeRig is intended for rig *authors* — people who want to create new rig definitions from scratch or modify existing ones, export them as JSON rig files, and manage the vertex weight files that accompany them.

MakeRig defines four panels (one root container plus three functional child panels). All four panels are parented to `MPFB_PT_Create_Panel` ("Create assets") and appear in the `RIGCATEGORY` sidebar tab.

## Panels

### MPFB_PT_MakeRig_Panel ("MakeRig")

| Attribute | Value |
|---|---|
| `bl_label` | "MakeRig" |
| `bl_category` | `RIGCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Create_Panel` |
| `bl_options` | `DEFAULT_CLOSED` |
| Base class | `Abstract_Panel` |

This is a container panel. It draws no controls of its own; its sole purpose is to provide the collapsible parent that groups the three functional MakeRig panels together in the sidebar.

---

### MPFB_PT_MakeRigBones_Panel ("Manage bones")

| Attribute | Value |
|---|---|
| `bl_label` | "Manage bones" |
| `bl_category` | `RIGCATEGORY` |
| `bl_parent_id` | `MPFB_PT_MakeRig_Panel` |
| `bl_options` | `DEFAULT_CLOSED` |
| Base class | `Abstract_Panel` |

Provides a tool for precisely positioning individual bone heads and tails to the centre of MPFB joint cubes. Joint cubes are small helper objects baked into the base mesh that mark anatomically significant joint locations (shoulder, elbow, knee, etc.). By snapping bone endpoints to these cubes you can ensure that the rig is always aligned correctly with any base mesh shape, regardless of applied morphs.

The "Move head/tail" box is shown only when:

- The active object is an armature.
- The armature is in Edit mode.
- Exactly one bone is selected.
- The basemesh is either a child of the armature or is also selected.

The two dropdowns (`head_cube`, `tail_cube`) list every available joint cube by name, plus special entries "Don't change" and "To closest". After choosing targets, pressing **Move to cubes** repositions the selected bone.

---

### MPFB_PT_MakeRigIO_Panel ("Load/Save rig")

| Attribute | Value |
|---|---|
| `bl_label` | "Load/Save rig" |
| `bl_category` | `RIGCATEGORY` |
| `bl_parent_id` | `MPFB_PT_MakeRig_Panel` |
| `bl_options` | `DEFAULT_CLOSED` |
| Base class | `Abstract_Panel` |

Handles reading and writing rig definition files (JSON) and vertex weight files (JSON). Three boxes are drawn:

- **Load/Save rig** — properties for controlling import/export behaviour (`rig_parent`, `rig_subrig`, `rig_save_rigify`, `rig_refit`) and buttons to load or save a rig JSON file.
- **Load/Save weights** — properties for weight export (`weights_mask`, `save_masks`, `save_evaluated`) and buttons to load or save a weights JSON file.
- **Save to library** — only shown when the active object is an armature. Name and identifying-bones fields, plus a "Save rig to library" button that installs the rig definition into the user's local asset library.

---

### MPFB_PT_MakeRigWeights_Panel ("Manage weights")

| Attribute | Value |
|---|---|
| `bl_label` | "Manage weights" |
| `bl_category` | `RIGCATEGORY` |
| `bl_parent_id` | `MPFB_PT_MakeRig_Panel` |
| `bl_options` | `DEFAULT_CLOSED` |
| Base class | `Abstract_Panel` |

Provides a tool for automatically transferring vertex weights from one rig/character combination to another. This is useful when a new rig layout needs weights seeded from an existing, already-weighted rig.

The "Transfer weights" box is shown only when:

- Exactly two armature objects are selected.
- The active object is one of the two armatures.
- Each armature has a basemesh as a child or nearby relative.

The panel labels which rig is the source (active) and which is the destination, then shows the **Auto transfer weights** button.

## Operators

### MPFB_OT_MoveBoneToCubeOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.move_bone_to_cube` |
| `bl_label` | "Move to cubes" |

Repositions the head and/or tail of the currently selected bone to the centre of the joint cubes specified by `head_cube` and `tail_cube`. Only available in armature Edit mode with exactly one bone selected.

---

### MPFB_OT_LoadRigOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_rig` |
| `bl_label` | "Load rig" |

Opens a file browser and imports a rig definition JSON file, creating an armature in the scene. The `rig_parent` and `rig_subrig` properties control whether the new rig is parented to an existing object or created as a sub-rig.

---

### MPFB_OT_SaveRigOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.save_rig` |
| `bl_label` | "Save rig" |

Opens a file browser and exports the active armature to a rig definition JSON file. The `rig_save_rigify` property controls whether Rigify layer metadata is included. The `rig_refit` property controls whether a refit operation is performed after saving.

---

### MPFB_OT_LoadWeightsOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_weights` |
| `bl_label` | "Load weights" |

Opens a file browser and imports a vertex weight JSON file onto the basemesh associated with the active armature.

---

### MPFB_OT_SaveWeightsOperator (makerig)

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.save_weights` |
| `bl_label` | "Save weights" |

Opens a file browser and exports the vertex weights of the basemesh associated with the active armature to a JSON file. The `weights_mask` property selects which rig the weights are exported for; `save_masks` controls whether mask vertex groups are included; `save_evaluated` controls whether the evaluated (post-modifier) mesh is used as the source.

---

### MPFB_OT_SaveRigToLibraryOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.save_rig_to_library` |
| `bl_label` | "Save rig to library" |

Saves the active armature as a named rig into the user's local MPFB asset library. The `library_rig_name` property sets the name; `library_identifying_bones` is a comma-separated list of bones that uniquely identify the rig type (used when auto-detecting a rig on import); `library_also_save_weights` controls whether the associated weight file is also written to the library.

---

### MPFB_OT_AutoTransferWeightsOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.auto_transfer_weights` |
| `bl_label` | "Auto transfer weights" |

Automatically copies vertex weights from the source rig's basemesh to the destination rig's basemesh. The source rig is the active armature; the destination is the other selected armature. Uses nearest-vertex mapping for the transfer.

## Properties

MakeRig uses `MakeRigProperties` (prefix `"MRP_"`), combining JSON-defined properties from `makerig/properties/` with several additional properties defined in code in `makerig/__init__.py`.

### From JSON files

| Property | Type | Description |
|---|---|---|
| `rig_parent` | boolean | Make the loaded rig the parent of the basemesh. |
| `rig_subrig` | boolean | Treat the loaded rig as a sub-rig rather than a primary rig. |
| `rig_save_rigify` | boolean | Include Rigify layer metadata when saving the rig. |
| `rig_refit` | boolean | Refit the rig to the basemesh after saving. |
| `weights_mask` | enum | Which rig type the weights are associated with (used to filter when multiple rigs are present). |
| `save_masks` | boolean | Include mask vertex groups in the exported weight file. |
| `save_evaluated` | boolean | Use the evaluated (post-modifier) mesh when exporting weights. |
| `head` | boolean | Update the head bone when repositioning. |

### Defined in code

| Property | Type | Description |
|---|---|---|
| `head_cube` | enum (dynamic) | Joint cube to snap the selected bone's head to. Populated from the base mesh's `joint-*` vertex groups. Special options: "Don't change" and "To closest". |
| `tail_cube` | enum (dynamic) | Joint cube to snap the selected bone's tail to. Same options as `head_cube`. |
| `library_rig_name` | string | Alphanumeric name (letters, digits, underscores) for the rig when saving to library. |
| `library_identifying_bones` | string | Comma-separated bone names that uniquely identify this rig type. |
| `library_also_save_weights` | boolean | Also save the associated weight file when saving the rig to library. Default: true. |

## Related

- [Rigging — Add Rig](../rigging/addrig.md) — apply a finished rig definition to a character
- [MakeWeight](makeweight.md) — standalone weight editing tools (truncation, symmetrisation, import/export)
- [RigService](../../services/rigservice.md) — the service underlying rig loading and saving
