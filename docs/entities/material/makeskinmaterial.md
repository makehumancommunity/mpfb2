# MakeSkinMaterial

## Overview

`MakeSkinMaterial` extends [`MhMaterial`](mhmaterial.md) and bridges the MHMAT format with Blender's node-based material system for the **MakeSkin workflow**.

See the [MHMAT file format reference](../../fileformats/mhmat.md) and [Material settings](../../fileformats/material_settings.md) for related format documentation.

### Import direction (MHMAT → Blender)

`apply_node_tree` loads the `makeskin.json` node-tree template from the MPFB data directory, substitutes `$variable` placeholders with texture paths and colour values derived from the current MHMAT settings, and applies the resulting node tree to a Blender material using `NodeService`.

### Export direction (Blender → MHMAT)

`populate_from_object` reads texture nodes and Principled BSDF socket values from an existing Blender object's node tree, populating `_settings` so that `as_mhmat` (inherited from `MhMaterial`) can serialise them. `export_to_disk` then writes the MHMAT file and optionally copies all referenced textures into the target directory with normalised names.

## Source

`src/mpfb/entities/material/makeskinmaterial.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `bpy` | Node tree access, image creation |
| `MhMaterial` | Base class |
| `MHMAT_KEYS` | Full key catalog for default values during `populate_from_object` |
| `LogService` | Logging via `LogService.get_logger("material.makeskinmaterial")` |
| `LocationService` | Locating the `makeskin.json` node-tree template and data directories |
| `NodeService` | Node tree application, node lookup, UV map node creation |
| `MaterialService` | Empty material creation |

## Public API

### `__init__(importer_presets=None)`

Initialise `MakeSkinMaterial` with optional importer preset values.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `importer_presets` | dict or None | `None` | Preset dictionary from the importer UI; stored in `self.presets` |

**Returns:** `None`.

---

### `apply_node_tree(blender_material, template_values=None)`

Apply the `makeskin.json` node-tree template to a Blender material.

If `template_values` is `None`, the method builds the dict automatically by scanning `self._settings` for each texture type (diffuse, normal map, bump map, AO, roughness map, metallic map, etc.) and colour values. Placeholders of the form `"$key"` in the JSON template are replaced with the computed values before the JSON is parsed.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_material` | `bpy.types.Material` | — | The Blender material whose node tree will be replaced |
| `template_values` | dict or None | `None` | Pre-built substitution dict; if `None`, built automatically from `self._settings` |

**Returns:** `None`.

**Raises:** `ValueError` if the JSON template cannot be parsed after variable substitution (indicates a malformed template value).

---

### `ensure_uvmap_node_for_texture_nodes(blender_object)`

Add a `ShaderNodeUVMap` node upstream of any texture node in the material that does not already have a UV input connected.

The new UV Map node is positioned 300 units to the left and 200 units below the texture node and linked to the object's first UV layer.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | Object whose first material slot provides the node tree |

**Returns:** `None`.

---

### `populate_from_object(blender_object)`

Extract material settings from an existing Blender object's node tree and populate `self._settings`.

Scans all recognised texture node names to set file paths. Reads socket values from `Principled BSDF` (base colour, metallic, IOR, roughness) and from the `diffuseIntensity` mix node if present. Reads SSS radius from `Principled BSDF` and `sss_enable` from `MakeSkinObjectProperties`. Metadata and miscellaneous settings are read from `MakeSkinObjectProperties` on the object.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | Object whose first material slot is the source |

**Returns:** `None`.

---

### `check_that_all_textures_are_saved(blender_object, mhmat_dir=None, mhmat_bn=None)`

Validate that every texture node in the material has a saved image on disk.

If a texture node has an unsaved image and both `mhmat_dir` and `mhmat_bn` are provided, the image is automatically saved to `<mhmat_dir>/<mhmat_bn>_<type>.png` and the corresponding `_settings` entry is updated.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | Object whose first material slot is checked |
| `mhmat_dir` | str or None | `None` | Target directory for auto-saving unsaved images |
| `mhmat_bn` | str or None | `None` | Base name prefix for auto-saved images |

**Returns:** `None` if all textures are saved; otherwise an error message `str` describing the first problem found.

---

### `export_to_disk(mhmat_path, normalize_textures=True)`

Write the material to disk as an MHMAT file, optionally normalising and copying all texture files.

When `normalize_textures=True`, each texture referenced in `_settings` is copied to the same directory as `mhmat_path` with a name derived from the MHMAT base name and texture type (e.g. `myshirt_diffuse.png`). The `_settings` entries are updated to the new basenames before serialisation.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mhmat_path` | str | — | Full path of the output `.mhmat` file |
| `normalize_textures` | bool | `True` | If `True`, copy and rename textures alongside the MHMAT file |

**Returns:** `None`.

---

### `create_makeskin_template_material(blender_object, scene, name="MakeSkinMaterial")` *(static)*

Create a new Blender material from the MakeSkin template, driven by `MAKESKIN_PROPERTIES` scene settings.

Scene properties control which texture slots are included (`create_<type>` flags) and the image resolution for new texture images. New blank images are created and assigned to the appropriate texture nodes for each enabled slot.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | Object that will receive the new material |
| `scene` | `bpy.types.Scene` | — | Scene providing `MAKESKIN_PROPERTIES` configuration |
| `name` | str | `"MakeSkinMaterial"` | Name for the new Blender material |

**Returns:** `None`.

**Raises:** `ValueError` if `blender_object` or `scene` is `None`.

---

## Examples

### Import: apply MHMAT to a Blender material

```python
import bpy
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial

mat = MakeSkinMaterial()
mat.populate_from_mhmat("/path/to/skin.mhmat")

blender_material = bpy.data.materials.new(name="SkinMaterial")
blender_material.use_nodes = True

mat.apply_node_tree(blender_material)
```

### Export: write a Blender material to an MHMAT file

```python
import bpy
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial

obj = bpy.context.active_object
mat = MakeSkinMaterial()
mat.populate_from_object(obj)

error = mat.check_that_all_textures_are_saved(
    obj,
    mhmat_dir="/path/to/output",
    mhmat_bn="myshirt"
)
if error:
    print("Problem:", error)
else:
    mat.export_to_disk("/path/to/output/myshirt.mhmat")
```
