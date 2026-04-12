# Create Assets — MakeClothes

**Source:** `src/mpfb/ui/create_assets/makeclothes/`

**Parent panel:** `MPFB_PT_Create_Panel` ("Create assets")

## Overview

MakeClothes is the tool for authoring MakeHuman clothing asset files from inside Blender. The end result is a set of files in the MakeHuman clothing format: a `.mhclo` file describing how the clothing mesh is fitted and weighted to the base mesh, an `.mhmat` material file, and an `.obj` mesh file. These files can then be installed into MPFB's asset library and loaded onto any character.

The workflow is multi-step and the panel is context-sensitive — different control boxes are shown depending on what is selected and which prerequisite steps have been completed:

1. **Create the xref cache** (once per machine) — builds a lookup table that maps every vertex of every possible base mesh pose to the base geometry. This is used during clothes fitting.
2. **Extract the clothing mesh** — if the clothing is based on one of the base mesh's helper vertex groups (e.g. a body part isolate), extract that group into a standalone mesh object.
3. **Mark the object type** — tell MakeClothes what type of asset the mesh represents (e.g. `Clothes`, `Eyes`, `Hair`).
4. **Configure metadata** — set the asset name, description, license, author, and UUID.
5. **Configure material** — review the material (must be a MakeSkin material) and decide whether to export it.
6. **Generate delete group** (optional) — mark which base mesh vertices should be hidden when the clothes are worn.
7. **Validate** — run the built-in clothes check to catch common geometry errors before export.
8. **Write files** — export the final `.mhclo` + `.mhmat` + `.obj`, either directly to the file system or into the user's local asset library.

The panel is only drawn when the active object is a mesh.

## Panels

### MPFB_PT_MakeClothes_Panel ("MakeClothes")

| Attribute | Value |
|---|---|
| `bl_label` | "MakeClothes" |
| `bl_category` | `CLOTHESCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Create_Panel` |
| `bl_options` | `DEFAULT_CLOSED` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"MC_"` |

The panel draws the following collapsible boxes, each conditional on the current selection state:

- **Basemesh xref** — shown whenever a mesh is active. Button to build the cross-reference cache.
- **Import legacy** — shown whenever a mesh is active. Imports object properties from old-format MakeClothes JSON files.
- **Extract clothes** — shown when the active object is the base mesh. Dropdown to pick a vertex group, and a button to extract it into a new standalone mesh.
- **Set object type** — shown when any mesh is active. Displays the current object type and lets the user change it.
- **Clothes props** — shown when a non-basemesh, non-skeleton mesh is selected. Fields for name, description, tag, license, author, homepage, username, and UUID (with a "Generate UUID" button).
- **Material** — shown for selected clothes objects. Reports whether the material is a supported MakeSkin or Game Engine material; shows the `save_material` toggle.
- **Delete group** — shown when exactly one basemesh and one clothes-type mesh are both selected. Lets the user pick and paint which base mesh vertices the garment should hide.
- **Check clothes** — shown when basemesh + clothes are both selected. Runs a validation pass and displays pass/fail for each individual check.
- **Write clothes** / **Write [type]** — shown when basemesh + clothes are both selected and the xref cache exists. Buttons to write directly to files or into the library.

## Operators

### MPFB_OT_BasemeshXrefOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.basemesh_xref` |
| `bl_label` | "Create xref cache" |
| Poll | `ANY_OBJECT_ACTIVE` |

Builds a cross-reference table mapping each base mesh vertex to its surrounding geometry. This is a one-time, expensive operation (up to ~30 seconds) that must be done before clothes can be written. The cache is stored in the MPFB user cache directory and is reused for all subsequent exports.

---

### MPFB_OT_ExtractClothesOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.extract_makeclothes_clothes` |
| `bl_label` | "Extract clothes" |
| Poll | `ANY_MESH_OBJECT_ACTIVE` |

Extracts the vertex group chosen in `available_groups` from the active base mesh into a new standalone mesh object. This is the starting point when the clothing asset is derived from one of the helper groups baked into the base mesh (such as the scalp or fingernail groups).

---

### MPFB_OT_LegacyMakeClothesImportOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.legacy_makeclothes_import` |
| `bl_label` | "Import legacy props" |
| Poll | `ANY_OBJECT_ACTIVE` |

Imports object-level metadata (name, description, license, etc.) from a legacy MakeClothes 1.x JSON properties file into the current object's MPFB object properties.

---

### MPFB_OT_MarkMakeClothesClothesOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.mark_makeclothes_clothes` |
| `bl_label` | "Change type" |
| Poll | `ANY_OBJECT_ACTIVE` |

Sets the MPFB object type on the active mesh to the value selected in the `object_type` property. This is required before the clothes can be written, because the type is embedded in the `.mhclo` file.

---

### MPFB_OT_GenUuidOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.genuuid` |
| `bl_label` | "Generate UUID" |

Generates and stores a new random UUID in the `uuid` object property of the active clothes mesh. Every MakeHuman asset should have a unique UUID so it can be unambiguously identified in asset databases.

---

### MPFB_OT_MakeClothesGenDeleteOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.makeclothes_gendelete` |
| `bl_label` | "Interpolate" |

Generates the delete-group data for the clothes. The delete group records which vertices of the base mesh should be hidden when the garment is worn, preventing z-fighting between the skin and the clothing geometry. Requires both the basemesh and the clothes mesh to be selected.

---

### MPFB_OT_CheckMakeClothesClothesOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.check_makeclothes_clothes` |
| `bl_label` | "Check" |

Runs a validation suite on the clothes mesh and stores the results in memory. The panel then displays pass/fail for each check:

- `is_valid_object`, `has_any_vertices`, `has_any_vgroups`
- `all_verts_have_max_one_vgroup`, `all_verts_have_min_one_vgroup`
- `all_verts_belong_to_faces`, `all_faces_same_type`
- `clothes_groups_exist_on_basemesh`, `objs_same_scale`
- `all_checks_ok` — overall pass/fail

Any warnings generated are also listed. Requires basemesh + clothes to be selected.

---

### MPFB_OT_WriteClothesLibraryOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.write_makeclothes_library` |
| `bl_label` | "Store in library" |
| Poll | `ANY_OBJECT_ACTIVE` |

Writes the clothes asset directly into the user's local MPFB asset library, making it immediately available for loading via the Apply Assets panel. Requires the xref cache to exist and both a basemesh and clothes mesh to be selected.

---

### MPFB_OT_WriteClothesOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.write_makeclothes_clothes` |
| `bl_label` | "Save as files" |
| Poll | `ANY_OBJECT_ACTIVE` |

Opens a file browser so the user can choose where to save the `.mhclo` file. The `.mhmat` and `.obj` files are written alongside it using the same base filename. Use this operator when you want to manage the output files manually rather than placing them directly in the library.

## Properties

### Scene properties (prefix `"MC_"`)

| Property | Type | Description |
|---|---|---|
| `available_groups` | enum (dynamic) | Vertex groups on the active basemesh that can be extracted to clothes. Populated at draw time; includes `body` plus helper groups (scalp, fingernails, etc.). |
| `object_type` | enum | The MakeHuman asset type to assign to the clothes mesh (e.g. `Clothes`, `Eyes`, `Hair`, `Eyebrows`). |
| `save_material` | boolean | Whether to include and export the material alongside the `.mhclo` file. |

### Object properties (stored per object)

These are defined in `makeclothes/objectproperties/` and stored via `MakeClothesObjectProperties`:

| Property | Description |
|---|---|
| `name` | Human-readable asset name embedded in the `.mhclo` file. |
| `description` | Short description of the asset. |
| `tag` | Tag string for categorisation. |
| `license` | License string (e.g. `CC0`). |
| `author` | Author name. |
| `homepage` | URL for the asset's homepage or portfolio. |
| `username` | MakeHuman community username of the author. |
| `uuid` | Unique identifier for the asset. |
| `delete_group` | Name of the vertex group on the clothes mesh used for delete-group generation. |
| `z_depth` | Z-depth priority for layering multiple clothes assets. |

## Related

- [makeskin.md](makeskin.md) — create the `.mhmat` material that MakeClothes can embed
- [Apply Assets](../apply_assets/index.md) — load the finished clothes asset onto a character
- [ClothesService](../../services/clothesservice.md) — the service used by clothes loading and fitting

