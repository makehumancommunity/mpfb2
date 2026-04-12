# Create Assets — MakeUp

**Source:** `src/mpfb/ui/create_assets/makeup/`

**Parent panel:** `MPFB_PT_Create_Panel` ("Create assets")

## Overview

MakeUp is the tool for adding cosmetic overlay layers — such as eyeshadow, blush, or lip colour — on top of an existing MakeSkin material. In MakeUp terminology these overlays are called **ink layers**. An ink layer is an additional texture that is composited over the base skin using a dedicated UV map, so that the makeup can be painted at a precise location on the body without affecting the main skin texture.

The system works through UV maps stored as compressed data files (`.gz`). Each UV map defines a specific **focus** region of the body — for example, just the face or just the hands. The MakeUp panel lets the user pick a focus, create the ink layer texture at a chosen resolution, and then write the finished ink data back to a file.

A separate **Developer** section contains lower-level tools for creating, importing, and exporting the underlying UV map data files. These are only needed by people who want to add new focus regions, not by end users applying makeup.

## Panel

### MPFB_PT_MakeUp_Panel ("MakeUp")

| Attribute | Value |
|---|---|
| `bl_label` | "MakeUp" |
| `bl_category` | `MATERIALSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Create_Panel` |
| `bl_options` | `DEFAULT_CLOSED` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"MAKU_"` |

The panel draws three collapsible boxes:

- **Create ink layer** — choose a focus UV map and resolution, then press "Create ink" to add a new ink layer to the material. The active object must be a basemesh with a MakeSkin material.
- **Write ink layer** — choose which ink layer number to write and give it a name, then press "Write ink layer" to save it.
- **MakeUP Developer** — tools for working with the raw UV map data: create, write, and import UV map `.gz` files. Intended for advanced users and rig/asset developers.

## Operators

### MPFB_OT_CreateInkOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.create_ink` |
| `bl_label` | "Create ink" |
| Poll | `ANY_MESH_OBJECT_ACTIVE` |

Adds a new ink layer to the active object's MakeSkin material. The `focus_name` property selects which UV map to use for the layer; if "full body focus" is chosen, the default full-body UV layout is used instead of a focused one. The `create_ink` and `resolution` properties control additional creation parameters. Only MakeSkin materials are supported.

---

### MPFB_OT_WriteInkLayerOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.write_ink_layer` |
| `bl_label` | "Write ink layer" |

Writes the ink layer selected by `layer_number` to a file, using `ink_layer_name` as the file name. The `layer_number` dropdown is dynamically populated based on how many ink layers the current material has.

---

### MPFB_OT_CreateUVMapOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.create_uv_map` |
| `bl_label` | "Create UV map" |

Creates a new UV map data structure for a custom focus region. This is a developer tool used when authoring new makeup focus areas.

---

### MPFB_OT_WriteUVMapOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.write_uv_map` |
| `bl_label` | "Write UV map" |

Exports a UV map data structure to a compressed `.gz` file. The `uv_map_name` property specifies the file name. Once written, the file can be installed into the MPFB data directory so it appears as a focus option in the "Create ink layer" box.

---

### MPFB_OT_ImportUVMapOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.import_uv_map` |
| `bl_label` | "Import UV map" |

Imports a UV map from a `.gz` file. Used during development to load and inspect existing UV map data.

## Properties

### Scene properties (prefix `"MAKU_"`)

| Property | Type | Description |
|---|---|---|
| `focus_name` | enum (dynamic) | Which UV focus map to use when creating an ink layer. Populated at draw time by scanning both the system and user `uv_layers` directories for `.gz` files. The first option is always "full body focus" (no specific UV map). |
| `layer_number` | enum (dynamic) | Which ink layer to write. Populated at draw time based on the number of ink layers in the active object's material. Only shown when the active object is a basemesh with a MakeSkin material that has at least one ink layer. |
| `create_ink` | boolean | Additional flag controlling ink layer creation behaviour. |
| `resolution` | integer/enum | Resolution in pixels for the ink layer texture. |
| `uv_map_name` | string | File name (without extension) for the UV map when using the developer export tools. |
| `ink_layer_name` | string | File name to use when writing an ink layer. |

## Related

- [MakeSkin](makeskin.md) — the MakeSkin material that ink layers are composited onto
- [MaterialService](../../services/materialservice.md) — the service used for material identification and ink layer counting
