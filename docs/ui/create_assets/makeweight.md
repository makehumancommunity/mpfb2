# Create Assets — MakeWeight

**Source:** `src/mpfb/ui/create_assets/makeweight/`

**Parent panel:** `MPFB_PT_Create_Panel` ("Create assets")

## Overview

MakeWeight is the tool for managing vertex weight files independently of any specific rig-attachment workflow. In the MakeHuman ecosystem, vertex weights describe how much each bone of a skeleton influences each vertex of the base mesh. These weights are stored as JSON files and are loaded alongside rig definitions when a rig is attached to a character.

MakeWeight lets you:

- **Import** an existing weight JSON file onto the active mesh, restoring the vertex groups it defines.
- **Export** the current vertex groups as a weight JSON file for redistribution or library storage.
- **Truncate** the weights in a selected vertex group, clamping small values to zero to clean up noisy weight paint data.
- **Symmetrize** weights from one side of the mesh to the other.

The panel is only drawn (poll passes) when the active object is a basemesh, a skeleton, or any object whose nearest relative in the scene hierarchy is a skeleton.

## Panel

### MPFB_PT_MakeWeight_Panel ("MakeWeight")

| Attribute | Value |
|---|---|
| `bl_label` | "MakeWeight" |
| `bl_category` | `MODELCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Create_Panel` |
| `bl_options` | `DEFAULT_CLOSED` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"MW_"` |

The panel draws three collapsible boxes:

- **Load and save** — buttons to import a weight JSON file and to save the current vertex groups as a weight JSON file.
- **Vertex groups** — a dropdown listing all non-joint vertex groups on the active object, and a "Truncate" button to clean up the selected group.
- **Symmetrize** — buttons to mirror weight values from the +X side to the -X side or vice versa.

## Operators

### MPFB_OT_ImportWeightsOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.import_makeweight_weight` |
| `bl_label` | "Import weights" |
| Poll | Active object must be a basemesh or skeleton |

Opens a file browser filtered to `.json` files and imports the chosen weight file onto the active mesh. The weight file defines vertex group names and per-vertex weight values; the operator creates or updates the corresponding vertex groups on the mesh.

---

### MPFB_OT_SaveWeightsOperator (makeweight)

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.save_makeweight_weight` |
| `bl_label` | "Save weights" |
| Poll | Active object must be a basemesh or skeleton |

Opens a file browser and exports the current vertex groups of the active mesh to a `.json` weight file. All non-joint vertex groups are included.

---

### MPFB_OT_TruncateWeightsOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.truncate_weights` |
| `bl_label` | "Truncate" |

Cleans up the vertex group selected by the `vertex_group` property by removing or zeroing out weight values that fall below a threshold. This is useful after painting weights manually, where small stray values can cause unwanted bone influences.

---

### MPFB_OT_SymmetrizeWeightLeftOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.symmetrize_makeweight_left` |
| `bl_label` | "Copy +x to -x" |

Mirrors weight values from the positive-X side of the mesh to the corresponding mirrored vertices on the negative-X side. Vertex matching uses the base mesh's built-in symmetry table.

---

### MPFB_OT_SymmetrizeWeightRightOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.symmetrize_makeweight_right` |
| `bl_label` | "Copy -x to +x" |

Mirrors weight values from the negative-X side of the mesh to the corresponding mirrored vertices on the positive-X side.

## Properties

### Scene properties (prefix `"MW_"`)

| Property | Type | Description |
|---|---|---|
| `vertex_group` | enum (dynamic) | Vertex groups currently present on the active object, excluding groups whose names begin with `joint-`. Populated at draw time. Used to select which group the "Truncate" operation acts on. |
| `overwrite` | boolean | If false, refuse to overwrite an existing weight file when saving. |

## Related

- [MakeRig](makerig.md) — load/save rig and weight files as part of the rig authoring workflow
- [Rigging — Add Rig](../rigging/addrig.md) — attaches a rig and its associated weight file to a character
