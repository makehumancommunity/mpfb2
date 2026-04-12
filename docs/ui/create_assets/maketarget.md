# Create Assets — MakeTarget

**Source:** `src/mpfb/ui/create_assets/maketarget/`

**Parent panel:** `MPFB_PT_Create_Panel` ("Create assets")

## Overview

MakeTarget is the tool for creating MakeHuman morph target files. A morph target (`.target` file) encodes a set of per-vertex offsets from the base mesh rest position. When applied at a given weight (0.0 to 1.0), each vertex is displaced by that fraction of its stored offset, allowing smooth interpolation between the base shape and the target shape.

Targets are used to drive all morphing in MPFB and MakeHuman — body proportions, facial features, age, weight, and so on. Authors can create custom targets and install them into the asset library so they appear as sliders in the Model panel.

The workflow is:

1. **Initialize a target** — creates a named shape key on the active mesh. The mesh is now in "target editing" mode.
2. **Edit the mesh** — move vertices in the shape key to define the morph. The base shape is preserved in the "Basis" key; only the target shape key is modified.
3. **Save the target** — export the vertex offsets to a `.target` file, optionally also writing a library copy.
4. **Symmetrize** (optional, basemesh only) — mirror the offsets from one side to the other.

The panel is only drawn when the active object has a known MPFB object type (as set by the `object_type` property) and that type is not "Skeleton". When no target shape key matching the `name` property exists, the panel shows initialization controls. Once the target exists, it switches to save/symmetrize/debug controls.

## Panel

### MPFB_PT_MakeTarget_Panel ("MakeTarget")

| Attribute | Value |
|---|---|
| `bl_label` | "MakeTarget" |
| `bl_category` | `TARGETSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Create_Panel` |
| `bl_options` | `DEFAULT_CLOSED` |
| Base class | `Abstract_Panel` |

The panel draws different boxes depending on state:

**When no target exists on the active mesh:**

- **Initialize** — name field and buttons to create a blank target, import a `.target` file, or import a proxy-specific `.ptarget` file.

**When a target already exists:**

- **Save as file** — buttons to write the target to a `.target` file and to write a proxy-specific `.ptarget` file.
- **Save to library** — button to write the target directly into the user's local asset library.
- **Symmetrize** — (basemesh only) buttons to copy left-side offsets to the right or vice versa.
- **Debug** — button to print the raw target data to the system console.

## Operators

### MPFB_OT_CreateTargetOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.create_maketarget_target` |
| `bl_label` | "Create target" |

Creates a new shape key on the active mesh using the name from the `name` object property. The shape key is initialised as a copy of the Basis shape (i.e. no offsets yet). The user can then switch to the new shape key and edit vertex positions to define the morph.

---

### MPFB_OT_ImportTargetOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.import_maketarget_target` |
| `bl_label` | "Import target" |

Opens a file browser and imports a `.target` file, applying the stored vertex offsets as a new shape key on the active mesh. This is useful for editing an existing target rather than starting from scratch.

---

### MPFB_OT_ImportPTargetOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.import_maketarget_ptarget` |
| `bl_label` | "Import proxy-specific target" |

Like "Import target", but imports a proxy-specific `.ptarget` file. Proxy targets apply offsets to a proxy mesh (e.g. a topology or a clothing item) rather than the full base mesh.

---

### MPFB_OT_WriteTargetOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.write_maketarget_target` |
| `bl_label` | "Save target" |

Opens a file browser and writes the current target shape key to a `.target` file. The file format is plain text: one line per affected vertex, with the vertex index followed by the X, Y, Z offset values.

---

### MPFB_OT_WritePTargetOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.write_maketarget_ptarget` |
| `bl_label` | "Save proxy-specific target" |

Writes the current target as a proxy-specific `.ptarget` file. Used when the morph is intended to apply to a proxy mesh rather than the full base mesh.

---

### MPFB_OT_WriteLibraryTargetOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.write_library_target` |
| `bl_label` | "Save target" (to library) |

Writes the current target directly into the user's local MPFB asset library, making it immediately available as a slider in the Model panel.

---

### MPFB_OT_SymmetrizeTargetLeftOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.symmetrize_maketarget_left` |
| `bl_label` | "Copy left to right" |

Copies vertex offsets from the left side of the base mesh (positive X) to the corresponding mirrored vertices on the right side (negative X). Only available when the active object is the base mesh.

---

### MPFB_OT_SymmetrizeTargetRightOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.symmetrize_maketarget_right` |
| `bl_label` | "Copy right to left" |

Copies vertex offsets from the right side of the base mesh (negative X) to the corresponding mirrored vertices on the left side (positive X).

---

### MPFB_OT_PrintTargetOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.print_maketarget_target` |
| `bl_label` | "Print target" |

Prints the raw vertex offset data of the current target shape key to the system console. Useful for debugging to verify which vertices are being affected and by how much.

## Properties

### Object properties (stored per object, via `MakeTargetObjectProperties`)

Defined in `maketarget/objectproperties/`:

| Property | Type | Description |
|---|---|---|
| `name` | string | The name of the target. Used both as the shape key name in Blender and as the basis for the exported file name. Must match an existing shape key name for the save/symmetrize controls to appear. |

## Related

- [Apply Assets](../apply_assets/index.md) — load installed targets onto a character as morphing sliders
- [TargetService](../../services/targetservice.md) — the service that handles target loading, saving, and application
- [Target file format](../../fileformats/target.md) — documentation of the `.target` file format
