# FaceService

## Overview

FaceService provides static methods for loading and interpolating facial animation shape keys onto MPFB characters. It owns all logic related to visemes and ARKit face units.

The two main operations are:

- Load sets of viseme or ARKit face unit targets as shape keys on a basemesh with `load_targets`.
- Propagate those shape keys from the basemesh to child clothes and body proxy meshes with `interpolate_targets`.

All methods are static.

**Supported facial animation standards:**

| Standard | Constant | Count |
|----------|----------|-------|
| Microsoft visemes | `MICROSOFT_VISEMES` | 22 shapes |
| Meta visemes | `META_VISEMES` | 15 shapes |
| ARKit face units | `ARKIT_FACEUNITS` | 52 shapes |

The module-level constant `SIGNIFICANT_SHIFT_MINIMUM = 0.0001` is used as a threshold when interpolating shape keys to child meshes. Vertex offsets smaller than this value are considered trivial and are discarded, keeping the resulting mesh data compact.

## Source

`src/mpfb/services/faceservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.faceservice")` |
| `TargetService` | Bulk-loading targets via `TargetService.bulk_load_targets` |
| `ObjectService` | Getting child lists via `ObjectService.get_list_of_children` |
| `ClothesService` | Resolving absolute MHCLO paths for child meshes during interpolation |
| `Mhclo` | Loading MHCLO vertex correspondence data for shape key interpolation |

## Public API

### load_targets(basemesh, load_microsoft_visemes=True, load_meta_visemes=False, load_arkit_faceunits=False)

Bulk-loads facial animation shape keys onto the basemesh from the installed target asset packs. Each selected group of targets is added at value `0.0` via `TargetService.bulk_load_targets`. At least one of the flags must be `True` for any targets to be loaded.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh to load targets onto |
| `load_microsoft_visemes` | `bool` | `True` | Load the 22 Microsoft viseme targets |
| `load_meta_visemes` | `bool` | `False` | Load the 15 Meta viseme targets |
| `load_arkit_faceunits` | `bool` | `False` | Load the 52 ARKit face unit targets |

**Returns:** None

**Raises:** Exception from `TargetService.bulk_load_targets` if a required target asset pack is not installed.

---

### interpolate_targets(basemesh)

Transfers viseme and face-unit shape keys from the basemesh to every child mesh that has an associated MHCLO file. For each child, MHCLO vertex correspondence data (three basemesh vertex indices and barycentric weights per child vertex) is used to compute interpolated offsets. A shape key is only created on the child if at least one vertex offset exceeds `SIGNIFICANT_SHIFT_MINIMUM`; otherwise the shape key is skipped to avoid noise.

Modifiers on the basemesh are temporarily disabled during interpolation to ensure vertex positions are read in rest pose, and then restored afterwards.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh whose shape keys are interpolated to children |

**Returns:** None

---

---

### configure_lip_sync(basemesh)

Maps loaded visemes02 (Meta/ARKit) shape keys to the Lip Sync addon's property slots, automating the ~15 manual dropdown selections that would otherwise be required in the Lip Sync panel.

The mapping is driven by the `VISEMES02_TO_LIPSYNC` constant. For each entry, the method sets `basemesh.lipsync2d_props.lip_sync_2d_viseme_shape_keys_<viseme_id>` to the corresponding shape key name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh to configure. Must have visemes02 loaded and Lip Sync initialised. |

**Returns:** `list` — A list of viseme IDs whose target shape key was not found on the mesh. An empty list means all mappings were applied successfully.

**Raises:**
- `ValueError` — if the Lip Sync addon (`iocgpoly_lip_sync`) is not enabled in Blender preferences.
- `ValueError` — if `lipsync2d_props` is absent or `lip_sync_2d_initialized` is `False` on the object.
- `ValueError` — if `viseme_sil` is not present in the mesh's shape keys (indicating visemes02 is not loaded).

---

## Constants

### SIGNIFICANT_SHIFT_MINIMUM

`SIGNIFICANT_SHIFT_MINIMUM = 0.0001`

Minimum vertex offset (in Blender units) for a shape key deformation to be considered significant. Used in `interpolate_targets` when deciding whether to create a shape key on a child mesh, and re-exported by `ExportService` for the same purpose during modifier baking.

---

### VISEMES02_TO_LIPSYNC

A `dict` mapping viseme slot IDs (used by the Lip Sync addon as property name suffixes) to the corresponding visemes02 shape key names loaded by `FaceService.load_targets`.

```python
VISEMES02_TO_LIPSYNC = {
    "sil": "viseme_sil",
    "PP":  "viseme_PP",
    "FF":  "viseme_FF",
    "TH":  "viseme_TH",
    "DD":  "viseme_DD",
    "kk":  "viseme_kk",
    "CH":  "viseme_CH",
    "SS":  "viseme_SS",
    "nn":  "viseme_nn",
    "RR":  "viseme_RR",
    "aa":  "viseme_aa",
    "E":   "viseme_E",
    "ih":  "viseme_I",   # shape key name differs from slot ID
    "oh":  "viseme_O",   # shape key name differs from slot ID
    "ou":  "viseme_U",   # shape key name differs from slot ID
    "UNK": "viseme_sil", # no dedicated shape key; falls back to silence
}
```

Three slot IDs have shape key names that differ from the slot ID itself:

| Slot ID | Shape key name | Note |
|---------|---------------|------|
| `ih` | `viseme_I` | Lip Sync uses abbreviated vowel label |
| `oh` | `viseme_O` | Lip Sync uses abbreviated vowel label |
| `ou` | `viseme_U` | Lip Sync uses abbreviated vowel label |

`UNK` (unknown phoneme) has no dedicated shape key and reuses `viseme_sil` (silence) as a fallback.

---

## Examples

### Load and Interpolate Microsoft Visemes

```python
import bpy
from mpfb.services.faceservice import FaceService

basemesh = bpy.context.active_object

# Load Microsoft viseme shape keys onto the basemesh
FaceService.load_targets(basemesh, load_microsoft_visemes=True)

# Propagate those shape keys to all child meshes with MHCLO data
FaceService.interpolate_targets(basemesh)
```

```
