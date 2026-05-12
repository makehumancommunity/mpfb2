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

### is_faceunits01_installed(force_recheck=False)

Returns `True` if the `faceunits01` ARKit asset pack appears to be installed.

The probe calls `TargetService.target_full_path("cheekPuff")` once per session and caches the result in a module-level sentinel. Pass `force_recheck=True` to bust the cache (used by tests, and by callers that just installed the pack at runtime). Note: the cache is process-scoped, so installing the pack mid-session will not flip the result until Blender is restarted, unless `force_recheck=True` is used.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `force_recheck` | `bool` | `False` | Re-probe even if a cached result is available |

**Returns:** `bool` — `True` if the pack is installed, `False` otherwise.

---

### set_expression(basemesh, expression_dict)

Applies a partial expression to the basemesh. Additive: face units that are not mentioned in the dict are left untouched. Use `clear_expression` to zero everything first.

For each `(face_unit_name, weight)` pair: validates that `face_unit_name` is in `ARKIT_FACEUNITS` (warns and skips otherwise); computes the matching `!ex-{name}` shape key name via `TargetService.expression_name_to_shapekey_name`; if the shape key already exists on the basemesh, sets its value; otherwise looks up the corresponding target via `TargetService.target_full_path` and loads it on demand at the requested weight (this is the path the composer uses for first-touch slider drags).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh object |
| `expression_dict` | `dict[str, float]` | — | Bare ARKit name → weight in [0, 1] |

**Returns:** None

---

### clear_expression(basemesh)

Sets every `!ex-{name}` shape key on the basemesh to `0.0`. Iterates over `ARKIT_FACEUNITS`; missing shape keys are silently ignored. Modeling shape keys (with the `$md-` prefix) and visemes are not touched.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh object |

**Returns:** None

---

### read_current_expression(basemesh)

Reads the current `!ex-` shape key values into a dict keyed by bare ARKit names. The returned dict always contains all 52 ARKIT_FACEUNITS keys; face units whose shape key is missing on the basemesh are reported as `0.0`. The composer uses this to populate sliders from the current basemesh state without missing entries.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh object |

**Returns:** `dict[str, float]` — Bare ARKit face unit name → current shape key value.

---

### save_expression(filename, expression_dict, metadata)

Serialises an expression to a JSON file (see [Expression file format](../fileformats/expression.md)). Filters zero-valued entries and rounds weights to four decimals for stable diffs. The `metadata` dict supplies the top-level fields (`name`, `description`, `tags`, `author`, `copyright`, `license`, `homepage`); missing keys are written with empty-string defaults (or an empty list for `tags`). `tags` may also be passed as a comma-separated string and will be split into a list.

If `filename` is a bare basename (no directory part), it is resolved under `LocationService.get_user_data("expressions")` and the directory is created on demand.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filename` | `str` | — | Output path. Bare names resolve under `<user_data>/expressions/` |
| `expression_dict` | `dict[str, float]` | — | Bare ARKit name → weight; zero entries are dropped |
| `metadata` | `dict` | — | Top-level metadata fields |

**Returns:** `str` — The absolute path actually written to.

**Raises:** `ValueError` — if `filename` is empty.

---

### load_expression(filename)

Loads an expression JSON file (see [Expression file format](../fileformats/expression.md)). Tolerant of missing optional fields: `description`, `tags`, `author`, `copyright`, `license`, `homepage` default to empty string (or empty list for `tags`). Unknown `face_units` keys produce a warning and are skipped. Unknown top-level keys are ignored (forward compatibility).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filename` | `str` | — | Path to the JSON file |

**Returns:** `tuple[dict[str, float], dict]` — `(expression_dict, metadata)`. `expression_dict` only contains face units whose names are members of `ARKIT_FACEUNITS`. `metadata` contains the seven top-level metadata fields with defaults.

**Raises:** `IOError` — if the file does not exist; `ValueError` — if the document is not a JSON object.

---

### list_available_expressions()

Scans every standard MPFB asset root under `expressions/` and returns one entry per discovered
`.json` file. When the same library-relative path is present in multiple roots, the higher-priority
root wins — matching the precedence rule for poses. Files that fail to parse are skipped with a
warning so a single malformed file does not break the picker.

**Returns:** `list[tuple[str, str, dict]]` — Each tuple is
`(absolute_path, library_relative_path, metadata)` where `metadata` is the dict returned by
`load_expression`.

---

### aggregate_expression_stack(stack)

Pure aggregation helper. Given a list of applied-expression rows (each
`{"asset": <library-relative path>, "weight": <float>}`), loads every referenced file via
`load_expression`, multiplies each face unit's loaded weight by the row weight, sums per face unit,
clamps to `[0, 1]`, and returns the result. Rows whose `asset` cannot be resolved on disk are
skipped with a warning. Used by `set_stack_weight`, `apply_expression_file`,
`rebuild_expression_stack`, and the human-preset deserialization path.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `stack` | `list[dict]` | — | Applied-expressions list (typically read from `basemesh["mpfb_applied_expressions"]`) |

**Returns:** `dict[str, float]` — `{face_unit_name: weight}` containing only non-zero entries.

---

### set_stack_weight(basemesh, asset_fragment, weight)

Entry point used by the expressions-library panel's per-slider update callbacks. Reads the
current stack from `basemesh["mpfb_applied_expressions"]`; if `weight <= 0.0`, drops any row
whose `asset` matches `asset_fragment`; otherwise upserts a row
`{"asset": asset_fragment, "weight": weight}` with latest-wins per asset. Writes the new
stack back (sorted by `asset`), re-aggregates via `aggregate_expression_stack`, and refreshes
the live `!ex-*` shape keys with a single `clear_expression` + `set_expression` pass.

Auto-refit is the caller's responsibility — the panel's update callback decides whether to
invoke `HumanService.refit` based on its own scene toggle.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh object |
| `asset_fragment` | `str` | — | Library-relative path of the expression file (the value stored in the stack's `asset` field) |
| `weight` | `float` | — | New slider value in `[0, 1]`; `0.0` removes the row |

**Returns:** `dict[str, float]` — The aggregated `{face_unit_name: weight}` dict that was written via `set_expression`.

**Raises:** `ValueError` — if `basemesh` is `None` or `asset_fragment` is empty.

---

### apply_expression_file(basemesh, filename, weight=1.0, append=True)

Low-level helper that validates a file via `load_expression`, updates the persistent stack on
the basemesh (`basemesh["mpfb_applied_expressions"]` — sorted by `asset`, latest-wins per asset),
re-aggregates the stack, and writes the result to the `!ex-*` shape keys via a single
`clear_expression` + `set_expression` pass.

The expressions-library panel drives the use-side through `set_stack_weight` rather than this
helper. `apply_expression_file` is retained for callers that want an absolute-path,
weight-and-append entry point.

The auto-refit / `HumanService.refit` call is intentionally not done here — that decision
belongs to the calling operator, which reads its panel's `auto_refit` toggle.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh object |
| `filename` | `str` | — | Absolute path to an expression JSON file |
| `weight` | `float` | `1.0` | Row weight for this expression |
| `append` | `bool` | `True` | If `True`, append/replace by asset. If `False`, replace the stack with a single row. |

**Returns:** `dict[str, float]` — The aggregated `{face_unit_name: weight}` dict that was written via `set_expression`.

**Raises:** `IOError` — if the file does not exist; `ValueError` — if `basemesh` is `None` or the file is not a JSON object.

---

### rebuild_expression_stack(basemesh)

Re-aggregates `basemesh["mpfb_applied_expressions"]` into live `!ex-*` shape-key values. Used
after the stack list itself has been mutated externally and the live face values need
refreshing.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh object |

**Returns:** `dict[str, float]` — The aggregated dict that was written.

---

### clear_applied_expressions(basemesh)

Empties the persistent stack (`basemesh["mpfb_applied_expressions"]`) and zeroes every
`!ex-*` shape key.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh object |

**Returns:** None

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

### EXPRESSION_FORMAT_VERSION

`EXPRESSION_FORMAT_VERSION = 1`

On-disk schema version for expression JSON files (see [Expression file format](../fileformats/expression.md)). Bumped when a backwards-incompatible change is made to the format.

---

### APPLIED_EXPRESSIONS_PROP

`APPLIED_EXPRESSIONS_PROP = "mpfb_applied_expressions"`

Name of the object-level property on the basemesh that stores the JSON-encoded persistent
expression stack. Each entry is `{"asset": "<library-relative path>", "weight": <float>}`,
sorted by `asset`. `set_stack_weight`, `apply_expression_file`,
`rebuild_expression_stack`, `clear_applied_expressions`, and the human-preset
serialize/deserialize path read and write this property. The composer panel does **not**
touch it — composer changes drive `!ex-*` shape keys directly and are transient unless saved
as a `.json`.

---

### FACEUNIT_REGIONS

`FACEUNIT_REGIONS: dict[str, list[str]]`

Region grouping for the 52 ARKit face units. Keys are region identifiers (`"brow"`, `"eye"`, `"cheek"`, `"jaw"`, `"mouth"`, `"nose"`, `"tongue"`); values are ordered lists of bare ARKit names belonging to each region. The `MakeExpression` composer panel uses this to render one slider box per region. Together, the lists are a partition of `ARKIT_FACEUNITS` — every name appears in exactly one region.

---

### FACEUNIT_DESCRIPTIONS

`FACEUNIT_DESCRIPTIONS: dict[str, str]`

One-sentence descriptions for each ARKit face unit, suitable for slider tooltips. Source: the ARKit blendshape reference at <https://pooyadeperson.com/the-ultimate-guide-to-creating-arkits-52-facial-blendshapes/>.

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
