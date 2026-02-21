# Mhclo

## Overview

`Mhclo` parses and serialises **MHCLO clothing files**. See the [MHCLO file format reference](../../fileformats/mhclo.md) for a complete description of the format.

### Vertex mapping

The core data held by an `Mhclo` instance is the vertex mapping stored in `self.verts`. Every entry describes how one clothes vertex is anchored to the base mesh:

- **Exact mapping** (`weights == (1, 0, 0)`): the clothes vertex is co-located with a single base-mesh vertex. The MHCLO line contains only that vertex index.
- **Weighted mapping**: the clothes vertex is expressed as a barycentric combination of three base-mesh vertices, plus an offset `Vector`. The MHCLO line contains the three vertex indices, three barycentric weights, and three offset components.

### Coordinate system

The MHCLO file format stores offsets in MakeHuman's coordinate system (Y-up, Z-depth). Blender uses Z-up. `load` and `write_mhclo` handle the swap transparently: on read, the raw `(d0, d1, d2)` offsets become `Vector((d0, -d2, d1))`; on write, Y and Z scale references are exchanged accordingly.

### Notes

- `set_scalings` is a stub; the body-part detection logic is marked `TODO` and has no effect.
- `clothes` (the loaded Blender mesh object) is **not** set by `__init__`; it is set by `load_mesh`.

## Source

`src/mpfb/entities/clothes/mhclo.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `mathutils.Vector` | Offset vectors in `self.verts` |
| `ObjectService` | Loading and saving wavefront OBJ files |
| `LogService` | Logging via `LogService.get_logger("entities.mhclo")` |
| `LocationService` | Locating the `hm08_config.json` mesh metadata file |

## Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `obj_file` | str or None | `None` | Absolute path to the OBJ mesh referenced in the `.mhclo` file |
| `x_scale` | tuple or None | `None` | `(vmin, vmax, scale)` for the X axis reference scale |
| `y_scale` | tuple or None | `None` | `(vmin, vmax, scale)` for the Y axis reference scale |
| `z_scale` | tuple or None | `None` | `(vmin, vmax, scale)` for the Z axis reference scale |
| `author` | str | `"unknown"` | Author metadata from the MHCLO header comment |
| `license` | str | `"CC0"` | License metadata from the MHCLO header comment |
| `name` | str | `"imported_cloth"` | Name key from the MHCLO body |
| `description` | str | `"no description"` | Description metadata from the MHCLO header comment |
| `basename` | str or None | `None` | Absolute file path minus the `.mhclo` extension; set by `load` |
| `weights_file` | str or None | `None` | Absolute path to the vertex bone weights file (`.mhw`) if declared |
| `material` | str or None | `None` | Absolute path to the linked `.mhmat` material file |
| `tags` | str | `""` | Comma-separated tag string accumulated from `tag` lines |
| `zdepth` | int | `50` | Z-depth rendering order hint |
| `first` | int | `0` | Starting clothes vertex index (always 0; reserved field from the format) |
| `verts` | dict[int, dict] | `{}` | Vertex mapping: key is clothes vertex index; value has `"verts"` (3-tuple of int), `"weights"` (3-tuple of float), `"offsets"` (`Vector`) |
| `delverts` | list[int] | `[]` | Base-mesh vertex indices to hide when clothes are applied |
| `delete` | bool | `False` | Whether any `delete_verts` section was found in the file |
| `delete_group` | str | `"Delete"` | Name of the deletion vertex group |
| `uuid` | str or None | `None` | UUID from the MHCLO file |
| `max_pole` | int or None | `None` | Maximum pole count, if declared |
| `clothes` | `bpy.types.Object` | *(not set by `__init__`)* | The loaded Blender mesh object; set by `load_mesh` |

## Public API

### `__init__()`

Initialise an empty `Mhclo` object with all fields set to their defaults. No file is read.

**Returns:** `None`.

---

### `load(mhclo_filename, *, only_metadata=False)`

Parse an MHCLO file from disk and populate the object's attributes.

Metadata fields (`author`, `license`, `description`) are extracted from comment lines. Vertex mapping (`verts`, `delverts`) is parsed from the body. If `only_metadata=True`, parsing stops after the metadata/header fields; the vertex sections are skipped.

The Y/Z coordinate swap is applied to offset vectors on read: raw `(d0, d1, d2)` → `Vector((d0, -d2, d1))`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mhclo_filename` | str | — | Absolute path to the `.mhclo` file to parse |
| `only_metadata` | bool | `False` | If `True`, skip vertex mapping data after reading metadata |

**Returns:** `None`.

**Raises:** `ValueError` if `mhclo_filename` is empty or falsy; `IOError` if the file does not exist.

---

### `load_mesh(context)`

Import the OBJ mesh referenced in `self.obj_file` into Blender and store the resulting object in `self.clothes`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `context` | `bpy.types.Context` | — | Current Blender context |

**Returns:** The newly created `bpy.types.Object`.

**Raises:** `ValueError` if `obj_file` is not set; `IOError` if the OBJ import fails.

---

### `get_weights_filename(suffix=None)`

Return the path of the vertex bone weights file derived from the MHCLO basename.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `suffix` | str or None | `None` | Optional suffix inserted between the basename and the `.mhw` extension |

**Returns:** A `str` of the form `<basename>[.<suffix>].mhw`.

---

### `set_scalings(context, human)`

Determine the body part this clothing item was designed for by comparing `self.x_scale` against known body-part dimension data from `hm08_config.json`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `context` | `bpy.types.Context` | — | Current Blender context |
| `human` | `bpy.types.Object` | — | The human base-mesh object |

**Returns:** `None`.

**Note:** The body-part detection is incomplete (stub). The matched `bodypart` variable is identified but never stored or acted upon.

---

### `write_mhclo(filename, also_export_mhmat=False, also_export_obj=True, reference_scale=None)`

Serialise the current state of this object to an MHCLO file on disk.

The vertex mapping is written with exact matches as single-index lines and weighted matches as 9-value lines. Delete-vertex ranges are run-length encoded with ` - ` separators. Y and Z scale references are exchanged to match the MakeHuman file convention.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filename` | str | — | Output path for the `.mhclo` file |
| `also_export_mhmat` | bool | `False` | If `True`, also write a `.mhmat` file alongside the MHCLO |
| `also_export_obj` | bool | `True` | If `True`, export `self.clothes` as a `.obj` file using `ObjectService` |
| `reference_scale` | dict or None | `None` | Dict with keys `xmin`, `xmax`, `x_scale`, `ymin`, `ymax`, `y_scale`, `zmin`, `zmax`, `z_scale`; written as `x_scale`/`y_scale`/`z_scale` lines |

**Returns:** `None`.

**Raises:** `ValueError` if `filename` is `None`, or if `also_export_mhmat` or `also_export_obj` is `True` and `self.clothes` has not been set.

---

## Examples

### Load metadata only

```python
from mpfb.entities.clothes.mhclo import Mhclo

mhclo = Mhclo()
mhclo.load("/path/to/shirt.mhclo", only_metadata=True)
print(mhclo.name, mhclo.author, mhclo.uuid)
```

### Full load and inspect vertex mapping

```python
from mpfb.entities.clothes.mhclo import Mhclo

mhclo = Mhclo()
mhclo.load("/path/to/shirt.mhclo")

for vert_idx, mapping in mhclo.verts.items():
    verts   = mapping["verts"]    # 3-tuple of base-mesh vertex indices
    weights = mapping["weights"]  # 3-tuple of barycentric weights
    offsets = mapping["offsets"]  # mathutils.Vector offset
    print(vert_idx, verts, weights, offsets)
```
