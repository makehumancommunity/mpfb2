# EnhancedSkinMaterial

## Overview

`EnhancedSkinMaterial` extends [`MhMaterial`](mhmaterial.md) and applies MPFB's **enhanced (PBR + subsurface scattering) skin shader** using an `enhanced_skin.json` node-group template.

See the [Material settings reference](../../fileformats/material_settings.md) for documentation of the preset values that control this shader.

### Template substitution

`apply_node_tree` loads `enhanced_skin.json` from the MPFB data directory, substitutes `$variable` placeholders (texture paths, roughness, SSS scale, group name) with values built by `default_settings`, and applies the resulting node tree via `NodeService`.

### SSS radius scale

The `sss_radius_scale` template variable is derived from the `scale_factor` importer preset:

| `scale_factor` value | `sss_radius_scale` |
|----------------------|--------------------|
| `"DECIMETER"` | `1` |
| `"CENTIMETER"` | `10` |
| any other value | `0.1` |

This compensates for different unit scales so that the subsurface scattering radius looks anatomically correct regardless of the scene's unit setup.

### SSS texture

A bundled `textures/sss.png` from the MPFB data directory is always included as the subsurface colour texture. Whether the SSS node group is active depends on the `skin_material_type` preset (types containing `"sss"` enable it).

## Source

`src/mpfb/entities/material/enhancedskinmaterial.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `bpy` | Material access |
| `MhMaterial` | Base class |
| `LogService` | Logging via `LogService.get_logger("material.enhancedskinmaterial")` |
| `LocationService` | Locating `enhanced_skin.json` and the `textures/sss.png` SSS map |
| `NodeService` | Applying the node tree from the parsed JSON dict |
| `MaterialService` | `get_skin_diffuse_color()` for the skin-tweak diffuse colour |

## Public API

### `__init__(importer_presets)`

Initialise `EnhancedSkinMaterial` with the required importer preset dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `importer_presets` | dict | — | Preset dictionary (required; no default). Must contain at least `"skin_material_type"`. Optionally `"scale_factor"` for SSS radius scaling. |

**Returns:** `None`.

---

### `default_settings(blender_material, group_name=None)`

Build and return the template-value dict used to substitute placeholders in `enhanced_skin.json`.

Derives texture paths from `self._settings` (diffuse texture, normal map). Sets `has_sss` based on whether `"sss"` appears in `skin_material_type`. Sets `sss_radius_scale` from `scale_factor`. Sets `Roughness` to `"0.5"` as the initial value (may be overridden by `skin_tweaks`). Sets `group_name` from the parameter, the material name, or the fallback `"mpfb_enhanced_skin"`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_material` | `bpy.types.Material` | — | Used to derive the node-group name when `group_name` is not supplied |
| `group_name` | str or None | `None` | Explicit name for the shader node group; if `None`, falls back to the material name |

**Returns:** A `dict[str, str]` mapping template variable names to their string values.

---

### `skin_tweaks(template_values, blender_material)`

Apply skin-specific adjustments to the template values and to the Blender material.

Sets `blender_material.diffuse_color` to the canonical skin diffuse colour from `MaterialService.get_skin_diffuse_color()`, and sets `template_values["Roughness"]` to `"0.45"` (slightly lower than the `"0.5"` default set by `default_settings`).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `template_values` | dict | — | The template dict produced by `default_settings`; modified in-place |
| `blender_material` | `bpy.types.Material` | — | The Blender material whose `diffuse_color` is updated |

**Returns:** `None`.

---

### `apply_node_tree(blender_material, tweaks="SKIN", group_name=None)`

Build template values, optionally apply skin tweaks, then load and apply the `enhanced_skin.json` node-tree template to the given Blender material.

Backslashes in all substitution values are normalised to forward slashes before replacement to avoid JSON parse errors on Windows paths.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_material` | `bpy.types.Material` | — | The Blender material whose node tree will be replaced |
| `tweaks` | str | `"SKIN"` | If `"SKIN"`, call `skin_tweaks` to adjust roughness and diffuse colour; any other value skips tweaks |
| `group_name` | str or None | `None` | Passed through to `default_settings` for node-group naming |

**Returns:** `None`.

---

## Examples

### Apply enhanced skin shader to a Blender material

```python
import bpy
from mpfb.entities.material.enhancedskinmaterial import EnhancedSkinMaterial

presets = {
    "skin_material_type": "enhanced_sss",
    "scale_factor": "DECIMETER"
}

mat = EnhancedSkinMaterial(presets)
mat.populate_from_mhmat("/path/to/skin.mhmat")

blender_material = bpy.data.materials.new(name="EnhancedSkin")
blender_material.use_nodes = True

mat.apply_node_tree(blender_material)
```

### Apply without skin tweaks (e.g. for clothing or eyes)

```python
mat.apply_node_tree(blender_material, tweaks="NONE")
```

### Use a specific node-group name

```python
mat.apply_node_tree(blender_material, group_name="MyCustomSkinGroup")
```
