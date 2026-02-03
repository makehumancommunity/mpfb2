# AssetService

AssetService manages operations related to discovering, cataloging, and caching MPFB assets. It provides utility functions to retrieve and update asset lists, find absolute paths, list specific asset types (.mhclo, .mhmat, .bvh, .proxy), find alternative materials, manage asset pack metadata, and scan asset repositories.

## Source

`src/mpfb/services/assetservice.py`

## Dependencies

- `LogService` — logging
- `LocationService` — data root and user directory paths
- `SystemService` — path normalization

## Public API

### find_asset_files_matching_pattern(asset_roots, pattern="*.mhclo")

Scan asset roots for files matching the specified glob pattern.

### find_asset_absolute_path(asset_path_fragment, asset_subdir="clothes")

Find the absolute path of an asset given a relative path fragment.

### list_mhclo_assets(asset_subdir="clothes")

Find all `.mhclo` assets in the specified subdirectory.

### list_mhmat_assets(asset_subdir="skins")

Find all `.mhmat` assets in the specified subdirectory.

### list_bvh_assets(asset_subdir="poses")

Find all `.bvh` assets in the specified subdirectory.

### list_ink_layer_assets(asset_subdir="ink_layers")

Find all ink layer JSON files in the specified subdirectory.

### list_proxy_assets(asset_subdir="proxymeshes")

Find all proxy assets in the specified subdirectory.

### alternative_materials_for_asset(asset_source, asset_subdir="clothes", exclude_default=True)

Find alternative material files for a given asset.

### get_available_data_roots()

Retrieve all available data root directories from various configured locations.

### get_asset_roots(asset_subdir="clothes")

Retrieve asset root directories for a specific subdirectory.

### update_asset_list(asset_subdir="clothes", asset_type="mhclo")

Update the cached asset list for a subdirectory and type.

### update_all_asset_lists()

Update all cached asset lists.

### get_asset_list(asset_subdir="clothes", asset_type="mhclo")

Retrieve the cached asset list, updating it if necessary.

### path_to_fragment(asset_full_path, relative_to_fragment=None, asset_subdir="clothes")

Convert an absolute asset path to a relative fragment path.

### have_any_pack_meta_data()

Check if any asset pack metadata has been installed.

### check_if_modern_makehuman_system_assets_installed()

Check if the system assets pack and `brown.mhmat` file are installed.

### rescan_pack_metadata()

Load pack metadata from JSON files in the asset directories.

### get_pack_names()

Retrieve the names of all available asset packs.

### system_assets_pack_is_installed()

Check if the `makehuman_system_assets` pack is installed.

### get_asset_names_in_pack(pack_name)

Retrieve asset names within a specified pack.

### get_asset_names_in_pack_pattern(pack_pattern)

Retrieve asset names in packs whose names match a pattern.

## Example

```python
from mpfb.services.assetservice import AssetService

clothes = AssetService.get_asset_list("clothes", "mhclo")
full_path = AssetService.find_asset_absolute_path("jeans/jeans.mhclo")
alt_mats = AssetService.alternative_materials_for_asset(full_path)
```
