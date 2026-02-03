# TargetService

TargetService manages "targets" — specialized shape keys used to morph MPFB human models. It handles creating, loading, saving, and converting between target files and Blender shape keys, and manages macro detail targeting which provides high-level human phenotype control (gender, age, muscle, weight, race, etc.).

## Source

`src/mpfb/services/targetservice.py`

## Dependencies

- `LogService` — logging
- `AssetService` — asset path discovery
- `LocationService` — data directory paths
- `ObjectService` — Blender object operations
- `GeneralObjectProperties`, `HumanObjectProperties` — custom property access

## Public API

### shapekey_is_target(shapekey_name)

Guess whether a shape key is a target based on its name.

### bake_targets(basemesh)

Apply all shape keys to the mesh geometry and remove them.

### translate_mhm_target_line_to_target_fragment(mhm_line)

Translate an MHM save file line to a target fragment path.

### target_full_path(target_name)

Retrieve the full file path of a target by name.

### create_shape_key(blender_object, shape_key_name, also_create_basis=True, create_from_mix=False)

Create a new shape key on an object.

### get_shape_key_as_dict(blender_object, shape_key_name, *, smaller_than_counts_as_unmodified=0.0001, only_modified_verts=True)

Convert a shape key to a dictionary of vertex offsets.

### shape_key_info_as_target_string(shape_key_info, include_header=True)

Convert shape key info to a `.target` format string.

### target_string_to_shape_key(target_string, shape_key_name, blender_object, *, reuse_existing=False)

Parse a target string and apply it as a shape key on an object.

### symmetrize_shape_key(blender_object, shape_key_name, copy_left_to_right=True)

Mirror vertex coordinates of a shape key across the X axis.

### get_target_stack(blender_object, exclude_starts_with=None, exclude_ends_with=None)

Retrieve the stack of targets from an object as a list of (name, value) tuples.

### has_any_shapekey(blender_object)

Check if the object has any shape keys.

### has_target(blender_object, target_name, also_check_for_encoded=True)

Check if the object has a specific shape key by name.

### get_target_value(blender_object, target_name)

Retrieve the current value of a specific shape key.

### set_target_value(blender_object, target_name, value, delete_target_on_zero=False)

Set the value of a specific shape key.

### bulk_load_targets(blender_object, target_stack, encode_target_names=False)

Bulk load multiple shape keys from a target stack list.

### load_target(blender_object, full_path, *, weight=0.0, name=None)

Load a shape key from a `.target` file.

### get_default_macro_info_dict()

Return a dictionary with default macro attribute values (gender, age, weight, etc.).

### get_macro_info_dict_from_basemesh(basemesh)

Retrieve macro info values stored on a basemesh object.

### calculate_target_stack_from_macro_info_dict(macro_info, cutoff=0.01)

Calculate a target stack from macro info values.

### get_current_macro_targets(basemesh, decode_names=True)

Retrieve the current macro targets applied to a basemesh.

### reapply_all_details(basemesh, remove_zero_weight_targets=True)

Reapply all detail targets to a basemesh.

### reapply_macro_details(basemesh, remove_zero_weight_targets=True)

Reapply only macro detail targets to a basemesh.

### encode_shapekey_name(original_name)

Encode a shape key name using predefined character substitutions.

### decode_shapekey_name(encoded_name)

Decode an encoded shape key name back to original.

### macrodetail_filename_to_shapekey_name(filename, encode_name=False)

Convert a macro detail filename to a shape key name.

### filename_to_shapekey_name(filename, *, macrodetail=False, encode_name=None)

Convert a filename to a shape key name.

### prune_shapekeys(blender_object, cutoff=0.0001)

Remove shape keys with weight below the cutoff value.

## Example

```python
from mpfb.services.targetservice import TargetService

TargetService.load_target(basemesh, "/path/to/nose-width.target", weight=0.5)
macro_info = TargetService.get_default_macro_info_dict()
macro_info["gender"] = 1.0  # female
TargetService.reapply_macro_details(basemesh)
```
