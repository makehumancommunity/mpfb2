# MHMAT key system

## Overview

The MHMAT key system is implemented across two source files that together form the parsing infrastructure used by [`MhMaterial`](mhmaterial.md):

- **`mhmatkeytypes.py`** — defines a type hierarchy of key-parser classes. Each class knows how to detect its key name (by case-insensitive prefix match against an input line) and parse its value.
- **`mhmatkeys.py`** — instantiates the complete catalog of MHMAT keys and builds the lookup dictionaries used at parse time.

See the [MHMAT file format reference](../../fileformats/mhmat.md) for the full format specification.

### Pattern

Each `MhMatKey` subclass handles one logical value type. When `MhMaterial` reads a line, it looks up the key name in `MHMAT_NAME_TO_KEY` for O(1) dispatch, then calls the matching key object's `parse` (or `parse_file`) method to extract the typed value.

Key names are matched **case-insensitively**: every key object stores `key_name_lower = key_name.lower()` and `line_matches_key` compares against the lowercased input line.

## Sources

- `src/mpfb/entities/material/mhmatkeytypes.py`
- `src/mpfb/entities/material/mhmatkeys.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `re` | Regular-expression parsing of MHMAT line values (standard library only — no service imports) |

## Key type hierarchy

Defined in `mhmatkeytypes.py`:

| Class | Value type | Notes |
|-------|------------|-------|
| `MhMatKey` | (abstract base) | Provides `line_matches_key`, abstract `parse`, and default `as_string` |
| `MhMatStringKey` | `str` | Everything after the key name on the line |
| `MhMatFileKey` | `str` | Path resolved relative to the MHMAT/MHCLO file location; use `parse_file(line, location)` instead of `parse` |
| `MhMatFloatKey` | `float` | Single float; formatted to 4 decimal places by `as_string` |
| `MhMatBooleanKey` | `bool` | Accepts `"true"`, `"t"`, or `"1"` as `True`; anything else as `False` |
| `MhMatColorKey` | `list[float]` | Three space-separated floats (R G B) |
| `MhMatStringShaderKey` | `list[str]` | `"key subkey value"` — returns `[subkey, value]` |
| `MhMatBooleanShaderKey` | `bool` | `"key subkey boolvalue"` — returns the parsed bool |

### `MhMatKey` public methods

| Method | Description |
|--------|-------------|
| `__init__(key_name, default_value=None, key_group="Various")` | Store the key name (and its lowercase form), default value, and group |
| `line_matches_key(input_line)` | Return `True` if the lowercased line starts with `key_name_lower` |
| `parse(input_line)` | Parse the value from the line; returns `(key_name, value)`. **Must be overridden** by subclasses — base raises `ValueError` |
| `as_string(value)` | Serialise a typed value back to a string for writing an MHMAT file; default returns `str(value)` |

`MhMatFileKey` replaces `parse` with `parse_file(input_line, location)` where `location` is the directory containing the MHMAT file, used to resolve relative texture paths.

## Module-level objects (`mhmatkeys.py`)

| Name | Type | Description |
|------|------|-------------|
| `MHMAT_KEY_GROUPS` | `list[str]` | Ordered category names: `"Metadata"`, `"Color"`, `"Texture"`, `"Intensity"`, `"SSS"`, `"Various"` |
| `MHMAT_KEYS` | `list[MhMatKey]` | Full ordered catalog of key instances, one per MHMAT key name |
| `MHMAT_ALIAS` | `dict[str, str]` | Legacy/alternative name → canonical name (e.g. `"albedoTexture"` → `"diffuseTexture"`) |
| `MHMAT_NAME_TO_KEY` | `dict[str, MhMatKey]` | Lowercase key name → key instance for O(1) lookup during parsing |
| `MHMAT_SHADER_KEYS` | `list[MhMatKey]` | Separate list of shader-related key instances (`shader`, `shaderParam litsphereTexture`, `shaderConfig *`) |

### Key groups and representative keys

| Group | Representative keys |
|-------|---------------------|
| Metadata | `tag`, `name`, `description`, `uuid`, `license`, `author` |
| Color | `diffuseColor`, `specularColor`, `emissiveColor`, `ambientColor` |
| Texture | `diffuseTexture`, `normalmapTexture`, `bumpmapTexture`, `roughnessmapTexture`, `metallicmapTexture`, … |
| Intensity | `diffuseIntensity`, `normalmapIntensity`, `bumpmapIntensity`, … |
| SSS | `sssEnabled`, `sssRScale`, `sssGScale`, `sssBScale` |
| Various | `roughness`, `opacity`, `metallic`, `transparent`, `backfaceCull`, … |

### `parse_alias(texture_name)`

Map a legacy or alternative key name to its canonical form.

| Argument | Type | Description |
|----------|------|-------------|
| `texture_name` | str | Key name to look up (case-insensitive) |

**Returns:** The canonical key name as a `str` if an alias exists; otherwise the original `texture_name` unchanged.

---

## Examples

### Look up a key by name

```python
from mpfb.entities.material.mhmatkeys import MHMAT_NAME_TO_KEY

key_obj = MHMAT_NAME_TO_KEY["diffusecolor"]
print(key_obj.key_name)        # "diffuseColor"
print(key_obj.default_value)   # [0.5, 0.5, 0.5]
print(key_obj.key_group)       # "Color"
```

### Parse a single MHMAT line

```python
from mpfb.entities.material.mhmatkeys import MHMAT_NAME_TO_KEY

line = "diffuseColor 0.8 0.6 0.4"
key_obj = MHMAT_NAME_TO_KEY["diffusecolor"]
name, value = key_obj.parse(line)
print(name, value)  # "diffuseColor" [0.8, 0.6, 0.4]
```

### Iterate all keys by group

```python
from mpfb.entities.material.mhmatkeys import MHMAT_KEY_GROUPS, MHMAT_NAME_TO_KEY

for group in MHMAT_KEY_GROUPS:
    print(f"\n=== {group} ===")
    for key_obj in MHMAT_NAME_TO_KEY.values():
        if key_obj.key_group == group:
            print(f"  {key_obj.key_name} (default: {key_obj.default_value})")
```

### Resolve an alias

```python
from mpfb.entities.material.mhmatkeys import parse_alias

canonical = parse_alias("albedoTexture")
print(canonical)  # "diffuseTexture"

unchanged = parse_alias("diffuseTexture")
print(unchanged)  # "diffuseTexture"
```
