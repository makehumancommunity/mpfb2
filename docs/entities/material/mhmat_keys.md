# MHMAT key system

## Overview

The MHMAT key system is implemented across two source files that together form the parsing infrastructure used by [`MhMaterial`](mhmaterial.md):

- **`mhmatkeytypes.py`** — defines a type hierarchy of key-parser classes. Each class knows how to detect its key name (by case-insensitive prefix match against an input line) and parse its value.
- **`mhmatkeys.py`** — instantiates the complete catalog of MHMAT keys and builds the lookup dictionaries used at parse time.

See the [MHMAT file format reference](../../fileformats/mhmat.md) for the full format specification.

### Pattern

Each `MhMatKey` subclass handles one logical value type. When `MhMaterial` reads a line, it looks up the key name in `MHMAT_NAME_TO_KEY` for O(1) dispatch, then calls the matching key object's `parse` (or `parse_file`) method to extract the typed value.

Key names are matched **case-insensitively**: every key object stores `key_name_lower = key_name.lower()` and `line_matches_key` compares against the lowercased input line.

### What a parser returns when it cannot read the line

Every `parse()` in the hierarchy returns `(key_name, None)` for a line its own regular expression does not match — and the key name on its own does satisfy `line_matches_key()` while failing `^([a-zA-Z]+)\s+(.*)$`, so a key line carrying **no value at all** is exactly that case. The `MhMatValue` alias keeps that `None` in the signatures, because `MhMaterial` reads the second element of the tuple without testing it in three places.

> **`MhMatFileKey.parse_file()` does not return `(key_name, None)` for such a line; it raises `AttributeError`.** Its four reads of the parsed value are unguarded, where every sibling `parse()` falls through to the return. So a line such as `diffuseTexture` with nothing after it aborts the whole material load. See [`MhMaterial`](mhmaterial.md) for the two matching faults on its side.

`MhMatFloatKey.parse()` is the other unguarded one, for a different reason: it calls `float()` on whatever follows the key name, with no `try`, so `roughness abc` raises `ValueError` out of the load rather than being reported as an unparseable line.

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
| `MhMatStringKey` | `str \| None` | Everything after the key name on the line |
| `MhMatFileKey` | `str` | Path resolved relative to the MHMAT/MHCLO file location. It does **not** override `parse`, which still raises; it adds `parse_file(line, location)` alongside it, and `MhMaterial` picks between the two on an `isinstance` test |
| `MhMatFloatKey` | `float \| None` | Single float; formatted to 4 decimal places by `as_string` |
| `MhMatBooleanKey` | `bool \| str \| None` | Accepts `"true"`, `"t"`, or `"1"` as `True`; any other non-empty value as `False`. A value which is whitespace only yields the empty string rather than `False`, which is why the declared type is wider than `bool`. Both are falsy, so no caller has ever had to care |
| `MhMatColorKey` | `list[float] \| None` | Three space-separated floats (R G B). A line with two or four floats does not match and yields `None` |
| `MhMatStringShaderKey` | `list[str] \| None` | `"key subkey value"` — returns `[subkey, value]`. Exactly two arguments; anything else yields `None` |
| `MhMatBooleanShaderKey` | `bool \| str \| None` | `"key subkey boolvalue"` — returns the parsed bool. The declared type matches `MhMatBooleanKey`'s, although this regex requires a non-whitespace third token and so cannot in fact produce the empty string |

### `MhMatKey` attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `key_name` | `str` | The canonical, correctly cased key name |
| `key_name_lower` | `str` | The same lowercased, which is what `line_matches_key` compares against |
| `default_value` | `Any` | The value the key takes when a material does not declare it. Its type follows the key class, which is why it is `Any` |
| `key_group` | `str` | One of `MHMAT_KEY_GROUPS`, deciding which section `as_mhmat` writes the key in |
| `blendMaterial` | `bool` | `MhMatFileKey` only. When set, the path is joined to the location even if it is absolute, because a blend material path continues into the structure of the file |

### `MhMatKey` public methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(key_name: str, default_value: Any = None, key_group: str = "Various") -> None` | Store the key name (and its lowercase form), default value, and group |
| `line_matches_key` | `(input_line: str \| None) -> bool` | Return `True` if the lowercased line starts with `key_name_lower`. A `None` or empty line answers `False` rather than raising, which is what the `str \| None` records |
| `parse` | `(input_line: str) -> tuple[str, MhMatValue]` | Parse the value from the line; returns `(key_name, value)`. **Must be overridden** by subclasses — base raises `ValueError`. Each override narrows the second element to its own value type |
| `as_string` | `(value: Any) -> str` | Serialise a typed value back to a string for writing an MHMAT file; default returns `str(value)`. `MhMatFloatKey` narrows the argument to `float` and `MhMatColorKey` to a `Sequence[float]`, since each reads the value in a way only its own type supports |

`MhMatFileKey` adds `parse_file(input_line: str, location: str) -> tuple[str, str]`, where `location` is the directory containing the MHMAT file, used to resolve relative texture paths. The two shader classes default `key_group` to `"Shader"` rather than `"Various"`, though every instance in `mhmatkeys.py` passes `"Shaders"` explicitly instead.

### `MhMatValue`

```python
MhMatValue = str | float | bool | list[float] | list[str] | None
```

Declared in `mhmatkeytypes.py`. Every value an `MhMatKey` subclass can parse out of a line, and the second element of the tuple the base `parse()` promises. A union rather than `Any` so that the `None` stays visible to callers — see "What a parser returns when it cannot read the line" above.

## Module-level objects (`mhmatkeys.py`)

| Name | Type | Description |
|------|------|-------------|
| `MHMAT_KEY_GROUPS` | `list[str]` | Ordered category names: `"Metadata"`, `"Color"`, `"Texture"`, `"Intensity"`, `"SSS"`, `"Various"` |
| `MHMAT_KEYS` | `list[MhMatKey]` | Full ordered catalog of key instances, one per MHMAT key name |
| `MHMAT_ALIAS` | `dict[str, str]` | Legacy/alternative name → canonical name (e.g. `"albedoTexture"` → `"diffuseTexture"`) |
| `MHMAT_NAME_TO_KEY` | `dict[str, MhMatKey]` | Lowercase key name → key instance for O(1) lookup during parsing |
| `MHMAT_SHADER_KEYS` | `list[MhMatKey]` | Separate list of shader-related key instances (`shader`, `shaderParam litsphereTexture`, `shaderConfig *`). **Nothing in MPFB imports it.** `MhMaterial` does not parse `shader` or `shaderConfig` lines at all and handles `shaderParam` through `MHMAT_KEYS`, so the list is a record of which shader lines the format defines rather than something the parser consults |

### Key groups and representative keys

| Group | Representative keys |
|-------|---------------------|
| Metadata | `tag`, `name`, `description`, `uuid`, `license`, `author` |
| Color | `diffuseColor`, `specularColor`, `emissiveColor`, `ambientColor` |
| Texture | `diffuseTexture`, `normalmapTexture`, `bumpmapTexture`, `roughnessmapTexture`, `metallicmapTexture`, … |
| Intensity | `diffuseIntensity`, `normalmapIntensity`, `bumpmapIntensity`, … |
| SSS | `sssEnabled`, `sssRScale`, `sssGScale`, `sssBScale` |
| Various | `roughness`, `opacity`, `metallic`, `transparent`, `backfaceCull`, … |

`MHMAT_KEY_GROUPS` deliberately omits the `"Shader"`/`"Shaders"` group the shader classes use, because no key in `MHMAT_KEYS` carries it — so `as_mhmat` never opens a section for one.

### `parse_alias(texture_name)`

Map a legacy or alternative key name to its canonical form.

| Argument | Type | Description |
|----------|------|-------------|
| `texture_name` | `str` | Key name to look up (case-insensitive) |

**Returns:** `str` — the canonical key name if an alias exists; otherwise the original `texture_name` unchanged.

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
