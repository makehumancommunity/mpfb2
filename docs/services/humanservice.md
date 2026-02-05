# HumanService

HumanService provides high-level utility functions for creating and managing human characters within MPFB. It handles creating human meshes, serializing and deserializing character data to JSON and MHM formats, adding rigs and clothes, setting skin materials, refitting characters, and managing human presets.

## Source

`src/mpfb/services/humanservice.py`

## Dependencies

- `LogService` — logging
- `ObjectService` — Blender object operations
- `TargetService` — shape key management
- `AssetService` — asset discovery
- `ClothesService` — clothes management
- `RigService` — rig management
- `NodeService` — shader node operations
- `MaterialService` — material management
- `LocationService` — path resolution
- `SystemService` — system utilities
- `HumanObjectProperties`, `GeneralObjectProperties` — custom property access
- `Mhclo`, `Rig` — entity classes

## Public API

### update_list_of_human_presets()

Update the list of human presets from the config directory.

### get_list_of_human_presets(as_list_enum=True, use_cache=True)

Return the list of human presets, optionally as a Blender enum list.

### serialize_to_json_string(basemesh, save_clothes=False)

Serialize a human character to a JSON string.

### serialize_to_json_file(basemesh, filename, save_clothes=False)

Serialize a human character to a JSON file.

### deserialize_from_dict(human_info, deserialization_settings)

Deserialize a human character from a dictionary.

### deserialize_from_json_file(filename, deserialization_settings)

Deserialize a human character from a JSON file.

### deserialize_from_mhm(filename, deserialization_settings)

Deserialize a human character from an MHM file.

### get_default_deserialization_settings()

Return the default deserialization settings dictionary.

### create_human(mask_helpers=True, detailed_helpers=True, extra_vertex_groups=True, feet_on_ground=True, scale=0.1, macro_detail_dict=None)

Create a new human basemesh with the specified settings.

### add_builtin_rig(basemesh, rig_name, *, import_weights=True, operator=None)

Add a built-in rig to a basemesh.

### add_mhclo_asset(mhclo_file, basemesh, asset_type="Clothes", ...)

Add an MHCLO asset (clothes, body part, etc.) to a basemesh.

### set_character_skin(mhmat_file, basemesh, bodyproxy=None, skin_type="ENHANCED_SSS", ...)

Set the skin material for a character from an `.mhmat` file.

### refit(blender_object)

Refit a character, adjusting the basemesh, clothes, and rig to match current targets.

### get_asset_sources_of_equipped_mesh_assets(basemesh)

Retrieve asset source paths of all equipped mesh assets on a basemesh.

### unload_mhclo_asset(basemesh, asset)

Unload and remove an MHCLO asset from a basemesh.

## Example

```python
from mpfb.services.humanservice import HumanService

basemesh = HumanService.create_human(scale=0.1, feet_on_ground=True)
HumanService.add_builtin_rig(basemesh, "default")
HumanService.serialize_to_json_file(basemesh, "/tmp/my_character.json")
```
