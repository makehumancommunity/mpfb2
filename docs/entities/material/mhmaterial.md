# MhMaterial

## Overview

`MhMaterial` is the core parser and serialiser for **MHMAT material files**. See the [MHMAT file format reference](../../fileformats/mhmat.md) for a complete description of the format.

Parsed key/value pairs are stored in the private `_settings` dict. Callers read values through `get_value` and produce MHMAT text through `as_mhmat`. Shader configuration lines (`shader`, `shaderConfig`, `shaderParam litsphereTexture`) are stored separately in `self.shader_config` and `self.lit_sphere`.

`MhMaterial` can be populated from two sources:

- **Disk file** — via `populate_from_mhmat`.
- **Running MakeHuman instance** — via `populate_from_body_material_socket_call` or `populate_from_proxy_material_socket_call` (requires MakeHuman to be running and the socket connection to be active).

`MhMaterial` is used as a base class by [`MakeSkinMaterial`](makeskinmaterial.md) and [`EnhancedSkinMaterial`](enhancedskinmaterial.md).

> **A malformed line can abort the whole load rather than being skipped.** `_parse_material_line` uses the value a key's own parser produced without testing the `None` that parser returns for a line it could not read (see [the key system](mhmat_keys.md)), in two places, and a third lives in the parser itself. All three are reachable from a hand-written `.mhmat`:
>
> | input | result |
> |-------|--------|
> | `shaderParam X` — any number of arguments other than exactly two | `TypeError: 'NoneType' object is not subscriptable` |
> | a `tag` line with no value, after an earlier `tag` line which had one | `TypeError: can only concatenate str (not "NoneType") to str` |
> | any texture or file key with no value, e.g. `diffuseTexture` alone | `AttributeError: 'NoneType' object has no attribute 'startswith'`, from `MhMatFileKey.parse_file()` |
> | a float key with a non-numeric value, e.g. `roughness abc` | `ValueError: could not convert string to float`, from `MhMatFloatKey.parse()` |
>
> An otherwise-unparseable line is logged as `Unparseable line:` and skipped, so these four are the exception rather than the rule.

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
| `_settings` | `dict[str, Any]` | Private dict mapping canonical key names to parsed values. The value type follows the key — see [`MhMatValue`](mhmat_keys.md) |
| `_shader_config` | `dict[str, Any]` | Private dict for raw shader config state. Never written or read after `__init__`; dead |
| `lit_sphere` | `dict[str, Any]` | Intended as the litsphere shader configuration. Never written anywhere in MPFB, so the `as_mhmat` branch which reads it never runs — and could not work as written, since it interpolates the dict itself into the path rather than a texture name. A litsphere parsed out of a `shaderParam` line goes to `_settings["litsphereTexture"]` instead, and is written by the ordinary key-group loop |
| `shader_config` | `dict[str, Any]` | Intended as the shader config flags (e.g. `ambientOcclusion`, `bump`), written as `shader_config` lines in `as_mhmat`. Also never written anywhere in MPFB, so that loop never runs either |
| `location` | `str` | Directory of the last `.mhmat` file read; set by `populate_from_mhmat`, used to resolve relative texture paths. Annotated on the class rather than assigned in `__init__`, because that is where the code puts it: an instance populated over the socket never has the attribute at all, and `_parse_material_line` — its only reader — is only ever reached through `populate_from_mhmat` |

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
| `file_name` | `str` | — | Path to the `.mhmat` file (absolute or resolvable by `os.path.abspath`) |

**Returns:** `None`.

---

### `populate_from_body_material_socket_call(load_mhmat_if_provided=False)`

Populate settings from the body material of a running MakeHuman instance via the socket API.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `load_mhmat_if_provided` | `bool` | `False` | If `True` and the response includes a `materialFile` path, load from that file instead of using the socket response values directly |

**Returns:** `None`.

A socket call MakeHuman declines answers with an empty payload, which arrives as `None` and is iterated without being tested, so a refused call raises `TypeError` here rather than reporting the reason MakeHuman sent with it.

---

### `populate_from_proxy_material_socket_call(uuid, load_mhmat_if_provided=False)`

Populate settings from a proxy (clothing/hair) material on a running MakeHuman instance, identified by its UUID.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `uuid` | `str` | — | UUID of the proxy asset in MakeHuman |
| `load_mhmat_if_provided` | `bool` | `False` | If `True` and the response includes a `materialFile` path, load from that file instead |

**Returns:** `None`.

Carries the same refused-call caveat as `populate_from_body_material_socket_call` above.

---

### `get_value(mhmat_key_name, case_insensitive=True)`

Retrieve a material setting by its canonical MHMAT key name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mhmat_key_name` | `str` | — | The key name to look up (e.g. `"diffuseColor"`, `"roughness"`) |
| `case_insensitive` | `bool` | `True` | If `True`, fall back to a case-insensitive scan when an exact match is not found |

**Returns:** `Any` — the stored value, whose type depends entirely on which key was asked for (`float`, `bool`, `list[float]`, `str`; see [`MhMatValue`](mhmat_keys.md)), or `None` if the key is absent or its value is falsy. `Any` is the deliberate answer here rather than a placeholder: the caller's own key argument decides the type.

Note that the test is on truthiness, not on `None`, so a key whose value is `0.0`, `False` or the empty string is reported as absent.

---

### `as_mhmat()`

Serialise the current material settings to an MHMAT-format string.

Keys are grouped by category in `MHMAT_KEY_GROUPS` order. Keys that have a value are written as `key value` lines; keys with `None` values are written as commented-out lines at the end. Multiple `tag` values are expanded to separate `tag` lines. Shader config is written after the main key groups.

**Returns:** `str` — a complete, human-readable MHMAT document.

The two shader blocks it writes after the key groups are both dead; see the `lit_sphere` and `shader_config` rows in Attributes above.

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
