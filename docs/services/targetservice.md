# TargetService

## Overview

TargetService manages "targets" — serialized shape keys used to morph MPFB human base meshes. A target is fundamentally a list of vertex indices paired with XYZ offset vectors describing how each vertex should be displaced when the target is applied. In Blender, targets are stored as shape keys with a one-to-one mapping between a target file and a shape key.

The service handles the full target lifecycle: creating shape keys, loading targets from `.target` or `.target.gz` files, converting between shape keys and target string formats, and managing the **macro target system**. Macro targets provide high-level phenotype control (gender, age, muscle, weight, race, proportions, height, cupsize, firmness) by interpolating between combinations of underlying shape keys according to a configuration defined in `macro.json`.

Because Blender limits shape key names to 61 characters, TargetService includes a name encoding/decoding system that abbreviates common terms (e.g., `macrodetail` to `$md`, `female` to `$fe`). All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/targetservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.targetservice")` |
| `AssetService` | Finding target files across asset root directories |
| `LocationService` | Resolving paths to system targets, custom targets, and UV layer data |
| `ObjectService` | Object type queries (for symmetrization validation) |
| `GeneralObjectProperties` | Reading scale factor from object custom properties |
| `HumanObjectProperties` | Reading macro attribute values (gender, age, etc.) from basemesh |
| `PrimitiveProfiler` | Performance profiling of target operations |

## Constants

### Shape Key Name Encoding

Pairs used to shorten shape key names to fit within Blender's 61-character limit:

| Original | Encoded |
|----------|---------|
| `macrodetail` | `$md` |
| `female` | `$fe` |
| `male` | `$ma` |
| `caucasian` | `$ca` |
| `asian` | `$as` |
| `african` | `$af` |
| `average` | `$av` |
| `weight` | `$wg` |
| `height` | `$hg` |
| `muscle` | `$mu` |
| `proportions` | `$pr` |
| `firmness` | `$fi` |
| `ideal` | `$id` |
| `uncommon` | `$un` |
| `young` | `$yn` |
| `child` | `$ch` |

### Macro Attributes

The macro target system uses these attributes, each with a default value of `0.5`:

`gender`, `age`, `muscle`, `weight`, `proportions`, `height`, `cupsize`, `firmness`

Plus a `race` sub-dictionary with `asian`, `caucasian`, and `african` (defaults: `0.33` each).

## Public API

### Shape Key Creation and Queries

#### create_shape_key(blender_object, shape_key_name, also_create_basis=True, create_from_mix=False)

Create a new shape key on a Blender object. If `also_create_basis` is `True` and no Basis shape key exists, one is created first. The new shape key's value is set to `1.0` and it becomes the active shape key.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The mesh object to add the shape key to |
| `shape_key_name` | `str` | — | Name for the new shape key |
| `also_create_basis` | `bool` | `True` | Create a Basis shape key if missing |
| `create_from_mix` | `bool` | `False` | Create from the current mix of existing shape keys |

**Returns:** `bpy.types.ShapeKey` — The newly created shape key.

---

#### has_any_shapekey(blender_object)

Check if a Blender object has any shape keys at all.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to check |

**Returns:** `bool` — `True` if the object has at least one shape key.

---

#### has_target(blender_object, target_name, also_check_for_encoded=True)

Check if a Blender object has a specific shape key, optionally checking the encoded form of the name as well.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to check |
| `target_name` | `str` | — | The shape key name to look for |
| `also_check_for_encoded` | `bool` | `True` | Also check the encoded version of the name |

**Returns:** `bool` — `True` if the shape key exists.

---

#### get_target_value(blender_object, target_name)

Retrieve the current value of a specific shape key.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to query |
| `target_name` | `str` | — | The shape key name |

**Returns:** `float` — The shape key value, or `0.0` if not found.

---

#### set_target_value(blender_object, target_name, value, delete_target_on_zero=False)

Set the value of a specific shape key. Optionally removes the shape key if the value is set to zero.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to modify |
| `target_name` | `str` | — | The shape key name |
| `value` | `float` | — | The value to set |
| `delete_target_on_zero` | `bool` | `False` | Remove the shape key if value is below `0.0001` |

**Returns:** None

**Raises:** `ValueError` if the object or target name is invalid, or the object has no shape keys.

---

#### get_target_stack(blender_object, exclude_starts_with=None, exclude_ends_with=None)

Retrieve all shape keys from an object as a list of name/value dictionaries. Automatically excludes the Basis shape key and any keys matching the exclusion filters.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The mesh object to query |
| `exclude_starts_with` | `str` | `None` | Exclude shape keys starting with this string (case-insensitive) |
| `exclude_ends_with` | `str` | `None` | Exclude shape keys ending with this string (case-insensitive) |

**Returns:** `list[dict]` — List of `{"target": name, "value": float}` dictionaries.

**Raises:** `ValueError` if the object is not a valid mesh.

---

#### shapekey_is_target(shapekey_name)

Guess whether a shape key is a MakeHuman target based on its name. Checks for macro detail prefixes (`$md`) and known opposite-pair patterns (e.g., `decr-incr`, `down-up`, `in-out`). May not identify custom targets or unusual names.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `shapekey_name` | `str` | — | The shape key name to check |

**Returns:** `bool` — `True` if the name matches known target patterns.

---

### Target Loading and Saving

#### load_target(blender_object, full_path, *, weight=0.0, name=None)

Load a shape key from a `.target` or `.target.gz` file and apply it to a Blender object. The shape key name is derived from the filename if not specified. Supports both plain text and gzip-compressed target files.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The mesh object to add the shape key to |
| `full_path` | `str` | — | Absolute path to the target file |
| `weight` | `float` | `0.0` | Initial value for the shape key |
| `name` | `str` | `None` | Custom name for the shape key (derived from filename if `None`) |

**Returns:** `bpy.types.ShapeKey` — The created shape key.

**Raises:** `ValueError` if the object or path is invalid. `IOError` if the file doesn't exist.

---

#### bulk_load_targets(blender_object, target_stack, encode_target_names=False)

Load multiple targets from a target stack list. Each entry must have `"target"` (name) and `"value"` (weight) keys. Target files are resolved via `target_full_path` and loaded in batch. Targets that cannot be resolved to a file path are skipped with a warning.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The mesh object to load targets onto |
| `target_stack` | `list[dict]` | — | List of `{"target": name, "value": weight}` dictionaries |
| `encode_target_names` | `bool` | `False` | Whether to encode target names |

**Returns:** None

---

#### target_full_path(target_name)

Search for a target file by name across system targets, custom targets, and all target directories. Returns the first match found.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `target_name` | `str` | — | The target name to search for |

**Returns:** `str` or `None` — The full file path, or `None` if not found.

---

#### bake_targets(basemesh)

Apply all current shape keys to the mesh geometry and remove them. Creates a temporary shape key from the current mix, removes all other shape keys, then removes the temporary one — leaving the mesh in its final deformed state with no shape keys.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The mesh object whose shape keys are to be baked |

**Returns:** None

---

#### prune_shapekeys(blender_object, cutoff=0.0001)

Remove shape keys with weight below the cutoff value. Only removes shape keys identified as targets (via `shapekey_is_target`). The Basis shape key is always preserved.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The mesh object to prune |
| `cutoff` | `float` | `0.0001` | Weight threshold below which shape keys are removed |

**Returns:** None

---

### Target/Shape Key Conversion

#### get_shape_key_as_dict(blender_object, shape_key_name, *, smaller_than_counts_as_unmodified=0.0001, only_modified_verts=True)

Convert a shape key to a dictionary representation containing vertex offsets. Offsets are computed relative to the Basis shape key and divided by the object's scale factor.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The mesh object containing the shape key |
| `shape_key_name` | `str` or `bpy.types.ShapeKey` | — | The shape key name or object |
| `smaller_than_counts_as_unmodified` | `float` | `0.0001` | Offset magnitude threshold below which vertices are considered unmodified |
| `only_modified_verts` | `bool` | `True` | If `True`, only include vertices with offsets above the threshold |

**Returns:** `dict` — `{"name": str, "vertices": [(index, x, y, z), ...]}`.

**Raises:** `ValueError` if the object has no shape keys or the named shape key doesn't exist.

---

#### shape_key_info_as_target_string(shape_key_info, include_header=True)

Convert a shape key info dictionary (as returned by `get_shape_key_as_dict`) to a `.target` file format string. The output uses MakeHuman's XZY coordinate order with negated Y.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `shape_key_info` | `dict` | — | Shape key info dictionary |
| `include_header` | `bool` | `True` | Whether to include the standard MakeTarget header |

**Returns:** `str` — Target file content string.

---

#### target_string_to_shape_key(target_string, shape_key_name, blender_object, *, reuse_existing=False)

Parse a target format string and apply it as a shape key on a Blender object. If `reuse_existing` is `True` and a shape key with the same name already exists, it is updated instead of creating a new one.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `target_string` | `str` | — | The target file content string |
| `shape_key_name` | `str` | — | Name for the shape key |
| `blender_object` | `bpy.types.Object` | — | The mesh object to apply the shape key to |
| `reuse_existing` | `bool` | `False` | Reuse an existing shape key with the same name |

**Returns:** `bpy.types.ShapeKey` — The created or updated shape key.

---

#### translate_mhm_target_line_to_target_fragment(mhm_line)

Parse a line from a MakeHuman Model (`.mhm`) save file and extract the target name and weight. Handles translation of opposite-pair terms (e.g., `decr|incr`) and directory prefixes.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mhm_line` | `str` | — | A line from an MHM file |

**Returns:** `dict` — `{"target": target_name, "value": weight}`.

---

### Shape Key Name Encoding

#### encode_shapekey_name(original_name)

Encode a shape key name by replacing common substrings with short codes to fit within Blender's 61-character limit.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `original_name` | `str` | — | The original shape key name |

**Returns:** `str` — The encoded name.

---

#### decode_shapekey_name(encoded_name)

Decode a previously encoded shape key name back to its original form.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `encoded_name` | `str` | — | The encoded shape key name |

**Returns:** `str` — The decoded name.

---

#### filename_to_shapekey_name(filename, *, macrodetail=False, encode_name=None)

Convert a target filename to a shape key name by stripping the file extension (`.target`, `.ptarget`, `.gz`). If `macrodetail` is `True` or `None` (auto-detect from path), prepends `macrodetail-`. Encoding is applied automatically for macro details or names exceeding 60 characters.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filename` | `str` | — | The filename to convert |
| `macrodetail` | `bool` or `None` | `False` | Whether the file is a macro detail. `None` for auto-detection |
| `encode_name` | `bool` or `None` | `None` | Whether to encode the name. `None` for automatic |

**Returns:** `str` — The shape key name.

---

#### macrodetail_filename_to_shapekey_name(filename, encode_name=False)

Convert a macro detail filename to a shape key name. Convenience wrapper around `filename_to_shapekey_name` with `macrodetail=True`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filename` | `str` | — | The macro detail filename |
| `encode_name` | `bool` | `False` | Whether to encode the resulting name |

**Returns:** `str` — The shape key name.

---

### Macro Target System

#### get_default_macro_info_dict()

Return a dictionary with default values for all macro attributes: gender, age, muscle, weight, proportions, height, cupsize, and firmness at `0.5`, with race values at `0.33` each.

**Returns:** `dict` — Default macro info dictionary.

---

#### get_macro_info_dict_from_basemesh(basemesh)

Read the current macro attribute values stored on a basemesh object's custom properties and return them as a macro info dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh to read values from |

**Returns:** `dict` — Macro info dictionary with current values.

---

#### calculate_target_stack_from_macro_info_dict(macro_info, cutoff=0.01)

Calculate the complete target stack from a macro info dictionary. This is the core of the macro target system — it interpolates across all combinations of gender, age, muscle, weight, race, height, proportions, cupsize, and firmness to produce a weighted list of target files that should be applied.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `macro_info` | `dict` | — | Macro info dictionary (uses defaults if `None`) |
| `cutoff` | `float` | `0.01` | Minimum weight threshold for including a target |

**Returns:** `list[list]` — List of `[target_name, weight]` pairs.

---

#### get_current_macro_targets(basemesh, decode_names=True)

Retrieve the names of all macro target shape keys currently on a basemesh (those starting with `$md`).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh to query |
| `decode_names` | `bool` | `True` | Whether to decode encoded shape key names |

**Returns:** `list[str]` — List of macro target names.

---

#### reapply_macro_details(basemesh, remove_zero_weight_targets=True)

Recalculate and reapply all macro detail targets to a basemesh. Sets existing macro targets to zero, calculates the required targets from the current macro info, loads any missing targets, and sets all target values. Optionally removes macro targets with zero weight.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh to update |
| `remove_zero_weight_targets` | `bool` | `True` | Remove macro targets with zero weight |

**Returns:** None

---

#### reapply_all_details(basemesh, remove_zero_weight_targets=True)

Reapply both macro details and all micro/custom detail targets to a basemesh. Saves the current non-macro target stack, reapplies macro details, removes and re-loads the micro targets.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh to update |
| `remove_zero_weight_targets` | `bool` | `True` | Remove macro targets with zero weight |

**Returns:** None

---

### Shape Key Manipulation

#### symmetrize_shape_key(blender_object, shape_key_name, copy_left_to_right=True)

Mirror the vertex coordinates of a shape key across the X axis using a predefined mirror table. Only works on Basemesh objects.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The basemesh object |
| `shape_key_name` | `str` | — | The shape key to symmetrize |
| `copy_left_to_right` | `bool` | `True` | If `True`, copy left side to right; if `False`, right to left |

**Returns:** None

**Raises:** `ValueError` if the object type is not `"Basemesh"`.

---

## Examples

### Loading and Applying Targets

```python
from mpfb.services.targetservice import TargetService

# Load a single target with a specific weight
TargetService.load_target(basemesh, "/path/to/nose-width.target", weight=0.5)

# Check if a target exists
if TargetService.has_target(basemesh, "nose-width-incr"):
    value = TargetService.get_target_value(basemesh, "nose-width-incr")
    print(f"Current value: {value}")
```

### Working with the Macro Target System

```python
from mpfb.services.targetservice import TargetService

# Get default macro info and modify it
macro_info = TargetService.get_default_macro_info_dict()
macro_info["gender"] = 1.0      # fully female
macro_info["age"] = 0.7         # older
macro_info["race"]["african"] = 1.0
macro_info["race"]["asian"] = 0.0
macro_info["race"]["caucasian"] = 0.0

# Calculate and examine the resulting target stack
target_stack = TargetService.calculate_target_stack_from_macro_info_dict(macro_info)
for name, weight in target_stack:
    print(f"{name}: {weight:.4f}")

# Or simply reapply macro details from the basemesh's current properties
TargetService.reapply_macro_details(basemesh)
```

### Exporting a Shape Key as a Target File

```python
from mpfb.services.targetservice import TargetService

# Convert a shape key to target format
shape_info = TargetService.get_shape_key_as_dict(basemesh, "my_custom_shape")
target_string = TargetService.shape_key_info_as_target_string(shape_info)

# Write to file
with open("/path/to/my_target.target", "w") as f:
    f.write(target_string)
```
