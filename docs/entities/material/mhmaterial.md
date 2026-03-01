# MhMaterial

## Overview

`MhMaterial` is the core parser and serialiser for **MHMAT material files**. See the [MHMAT file format reference](../../fileformats/mhmat.md) for a complete description of the format.

Parsed key/value pairs are stored in the private `_settings` dict. Callers read values through `get_value` and produce MHMAT text through `as_mhmat`. Shader configuration lines (`shader`, `shaderConfig`, `shaderParam litsphereTexture`) are stored separately in `self.shader_config` and `self.lit_sphere`.

`MhMaterial` can be populated from two sources:

- **Disk file** — via `populate_from_mhmat`.
- **Running MakeHuman instance** — via `populate_from_body_material_socket_call` or `populate_from_proxy_material_socket_call` (requires MakeHuman to be running and the socket connection to be active).

`MhMaterial` is used as a base class by [`MakeSkinMaterial`](makeskinmaterial.md) and [`EnhancedSkinMaterial`](enhancedskinmaterial.md).

## Source

`src/mpfb/entities/material/mhmaterial.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `SocketService` | Fetching material info from a running MakeHuman instance |
| `LogService` | Logging via `LogService.get_logger("material.mhmaterial")` |
| `mhmatkeys` module | `MHMAT_NAME_TO_KEY`, `MHMAT_KEY_GROUPS`, `parse_alias` for parsing and serialisation |
| `MhMatFileKey` | Detection of file-type keys requiring path resolution |

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_settings` | `dict[str, any]` | Private dict mapping canonical key names to parsed values |
| `_shader_config` | `dict` | Private dict for raw shader config state (partially used) |
| `lit_sphere` | `dict` | Litsphere shader configuration; written as `shaderParam litsphereTexture` in `as_mhmat` |
| `shader_config` | `dict` | Shader config flags (e.g. `ambientOcclusion`, `bump`); written as `shader_config` lines in `as_mhmat` |
| `location` | str | Directory of the last `.mhmat` file read; set by `populate_from_mhmat`, used to resolve relative texture paths |

## Public API

### `__init__()`

Initialise an empty `MhMaterial` with no settings, no shader config, and no lit-sphere data.

**Returns:** `None`.

---

### `populate_from_mhmat(file_name)`

Read and parse an MHMAT file from disk.

Lines starting with `#` or `/` are treated as comments and skipped. Each remaining line is dispatched to the appropriate `MhMatKey` subclass in `MHMAT_NAME_TO_KEY`. Unknown key names are logged as warnings. Multiple `tag` lines are accumulated into a single comma-separated string. `shaderParam litsphereTexture` is stored in `self._settings["litsphereTexture"]`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `file_name` | str | — | Path to the `.mhmat` file (absolute or resolvable by `os.path.abspath`) |

**Returns:** `None`.

---

### `populate_from_body_material_socket_call(load_mhmat_if_provided=False)`

Populate settings from the body material of a running MakeHuman instance via the socket API.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `load_mhmat_if_provided` | bool | `False` | If `True` and the response includes a `materialFile` path, load from that file instead of using the socket response values directly |

**Returns:** `None`.

---

### `populate_from_proxy_material_socket_call(uuid, load_mhmat_if_provided=False)`

Populate settings from a proxy (clothing/hair) material on a running MakeHuman instance, identified by its UUID.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `uuid` | str | — | UUID of the proxy asset in MakeHuman |
| `load_mhmat_if_provided` | bool | `False` | If `True` and the response includes a `materialFile` path, load from that file instead |

**Returns:** `None`.

---

### `get_value(mhmat_key_name, case_insensitive=True)`

Retrieve a material setting by its canonical MHMAT key name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mhmat_key_name` | str | — | The key name to look up (e.g. `"diffuseColor"`, `"roughness"`) |
| `case_insensitive` | bool | `True` | If `True`, fall back to a case-insensitive scan when an exact match is not found |

**Returns:** The stored value (type depends on the key — `float`, `bool`, `list[float]`, `str`, etc.), or `None` if the key is absent or its value is `None`.

---

### `as_mhmat()`

Serialise the current material settings to an MHMAT-format string.

Keys are grouped by category in `MHMAT_KEY_GROUPS` order. Keys that have a value are written as `key value` lines; keys with `None` values are written as commented-out lines at the end. Multiple `tag` values are expanded to separate `tag` lines. Shader config is written after the main key groups.

**Returns:** A `str` containing a complete, human-readable MHMAT document.

---

## Examples

### Load from a file and read a colour value

```python
from mpfb.entities.material.mhmaterial import MhMaterial

mat = MhMaterial()
mat.populate_from_mhmat("/path/to/skin.mhmat")

color = mat.get_value("diffuseColor")
print(color)  # e.g. [0.63, 0.48, 0.38]

roughness = mat.get_value("roughness")
print(roughness)  # e.g. 0.7
```
