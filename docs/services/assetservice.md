# AssetService

## Overview

AssetService manages the discovery, cataloging, and caching of MPFB asset files across multiple data root directories. It provides the primary interface for locating assets (clothes, skins, eyes, hair, poses, etc.) stored on disk and for managing asset pack metadata.

MPFB assets are organized in a hierarchy of data roots: the built-in MPFB data directory, the MakeHuman user directory, the MPFB user directory, and an optional secondary root. Within each root, assets are grouped by subdirectory (e.g., `clothes`, `skins`, `eyes`, `poses`). AssetService scans these locations, resolves file paths, and maintains a cached dictionary of discovered assets with their metadata and thumbnail previews.

The service also manages **asset packs** — bundles of assets distributed as downloadable packages. Pack metadata is stored as JSON files in the user's `packs` directory and can be queried to determine which assets are installed and available. All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/assetservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.assetservice")` |
| `LocationService` | Resolving data roots (user data, MakeHuman data, MPFB data, secondary root) |
| `SystemService` | Path segment matching for alternative material discovery |

## Constants

### ASSET_LIBRARY_SECTIONS

A module-level list of 11 dictionaries, each defining an asset library section. Each dictionary contains:

| Key | Type | Description |
|-----|------|-------------|
| `bl_label` | `str` | Display name for the library section |
| `asset_subdir` | `str` | Subdirectory name within data roots |
| `asset_type` | `str` | File extension to scan for (e.g., `"mhclo"`, `"mhmat"`, `"bvh"`) |
| `object_type` | `str` | MPFB object type for loaded assets |
| `eye_overrides` | `bool` | Whether the section supports eye material overrides |
| `skin_overrides` | `bool` | Whether the section supports skin material overrides |

The sections cover: Topologies, Skins, Ink layers, Eyes, Eyebrows, Eyelashes, Hair, Teeth, Tongue, Clothes, and Poses.

## Public API

### Asset Discovery

#### find_asset_files_matching_pattern(asset_roots, pattern="*.mhclo")

Recursively scan the given asset root directories for files matching the specified glob pattern.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_roots` | `list[str]` | — | A list of root directories to scan |
| `pattern` | `str` | `"*.mhclo"` | The glob pattern to match files against |

**Returns:** `list[Path]` — A list of `Path` objects for matching files.

**Raises:** `IOError` if any root directory is `"/"` (prevents scanning entire filesystem).

---

#### find_asset_absolute_path(asset_path_fragment, asset_subdir="clothes")

Find the absolute path of an asset given a relative path fragment. The fragment can be a bare filename or a `parent_dir/filename` pair. When multiple matches exist, the method prefers the one whose parent directory matches the fragment.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_path_fragment` | `str` | — | The relative path fragment to search for |
| `asset_subdir` | `str` | `"clothes"` | The asset subdirectory to search within |

**Returns:** `str` or `None` — The absolute path to the asset, or `None` if not found.

---

#### list_mhclo_assets(asset_subdir="clothes")

Find all `.mhclo` asset files in the specified subdirectory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_subdir` | `str` | `"clothes"` | The asset subdirectory to search |

**Returns:** `list[Path]` — List of matching `.mhclo` files.

---

#### list_mhmat_assets(asset_subdir="skins")

Find all `.mhmat` asset files in the specified subdirectory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_subdir` | `str` | `"skins"` | The asset subdirectory to search |

**Returns:** `list[Path]` — List of matching `.mhmat` files.

---

#### list_bvh_assets(asset_subdir="poses")

Find all `.bvh` asset files in the specified subdirectory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_subdir` | `str` | `"poses"` | The asset subdirectory to search |

**Returns:** `list[Path]` — List of matching `.bvh` files.

---

#### list_ink_layer_assets(asset_subdir="ink_layers")

Find all ink layer JSON files in the specified subdirectory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_subdir` | `str` | `"ink_layers"` | The asset subdirectory to search |

**Returns:** `list[Path]` — List of matching `.json` files.

---

#### list_proxy_assets(asset_subdir="proxymeshes")

Find all `.proxy` asset files in the specified subdirectory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_subdir` | `str` | `"proxymeshes"` | The asset subdirectory to search |

**Returns:** `list[Path]` — List of matching `.proxy` files.

---

#### alternative_materials_for_asset(asset_source, asset_subdir="clothes", exclude_default=True)

Find alternative `.mhmat` material files for a given asset. Searches for materials in the same parent directory as the asset. For eye assets, also searches the `materials` subdirectory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_source` | `str` | — | The source path fragment of the asset |
| `asset_subdir` | `str` | `"clothes"` | The asset subdirectory to search within |
| `exclude_default` | `bool` | `True` | Whether to exclude the default material |

**Returns:** `list[str]` — List of absolute paths to alternative material files.

---

### Data Root Management

#### get_available_data_roots()

Retrieve all available data root directories. Checks four locations in order: MPFB built-in data, MakeHuman user data, MPFB user data, and the secondary root. Only directories that exist on disk are included.

**Returns:** `list[str]` — List of valid data root paths.

---

#### get_asset_roots(asset_subdir="clothes")

Retrieve asset root directories for a specific subdirectory by appending the subdirectory name to each available data root and filtering to those that exist.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_subdir` | `str` | `"clothes"` | The subdirectory to look for within each data root |

**Returns:** `list[str]` — List of existing asset root paths.

---

### Asset List Caching

#### update_asset_list(asset_subdir="clothes", asset_type="mhclo")

Scan an asset subdirectory for files of the given type and update the global asset list cache. Each cached entry contains `full_path`, `basename`, `dirname`, `fragment`, `name_without_ext`, `label`, and optional `thumb`/`thumb_path` for thumbnail previews.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_subdir` | `str` | `"clothes"` | The subdirectory to scan |
| `asset_type` | `str` | `"mhclo"` | The file extension to scan for |

**Returns:** None

---

#### update_all_asset_lists()

Update the global asset list cache for all sections defined in `ASSET_LIBRARY_SECTIONS`.

**Returns:** None

---

#### get_asset_list(asset_subdir="clothes", asset_type="mhclo")

Retrieve the cached asset list for a subdirectory and type. If the list is not yet cached, it is built automatically by calling `update_asset_list`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_subdir` | `str` | `"clothes"` | The subdirectory to retrieve |
| `asset_type` | `str` | `"mhclo"` | The file extension type |

**Returns:** `dict` — Dictionary mapping asset labels to asset info dictionaries.

---

#### path_to_fragment(asset_full_path, relative_to_fragment=None, asset_subdir="clothes")

Convert an absolute asset path to a relative fragment of the form `parent_dir/filename`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_full_path` | `str` | — | The absolute path to convert |
| `relative_to_fragment` | `str` | `None` | Reserved for future use |
| `asset_subdir` | `str` | `"clothes"` | The asset subdirectory |

**Returns:** `str` — The fragment path.

**Raises:** `NotImplementedError` if `relative_to_fragment` is provided.

---

### Asset Pack Metadata

#### have_any_pack_meta_data()

Check if any asset pack metadata JSON files exist in the user's `packs` directory.

**Returns:** `bool` — `True` if at least one `.json` file exists in the packs directory.

---

#### check_if_modern_makehuman_system_assets_installed()

Check whether the MakeHuman system assets pack is installed and whether it includes the `brown.mhmat` eye material (which indicates a modern version of the pack).

**Returns:** `tuple[bool, bool]` — `(system_assets_installed, brown_mhmat_installed)`.

---

#### rescan_pack_metadata()

Reload all asset pack metadata from JSON files in the user's `packs` directory. This always performs a fresh scan, replacing any previously cached metadata.

**Returns:** None

---

#### get_pack_names()

Retrieve a sorted list of all available asset pack names. Triggers a rescan if metadata has not been loaded yet.

**Returns:** `list[str]` — Sorted list of pack names.

---

#### system_assets_pack_is_installed()

Check if the `makehuman_system_assets` pack is present in the list of installed packs.

**Returns:** `bool` — `True` if the system assets pack is installed.

---

#### get_asset_names_in_pack(pack_name)

Retrieve a sorted list of all asset names within a specified pack.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `pack_name` | `str` | — | The name of the pack to query |

**Returns:** `list[str]` — Sorted list of asset names.

---

#### get_asset_names_in_pack_pattern(pack_pattern)

Retrieve asset names from all packs whose names contain the given pattern (case-insensitive substring match).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `pack_pattern` | `str` | — | Pattern to match against pack names |

**Returns:** `list[str]` — Sorted list of asset names from all matching packs.

---

## Examples

### Discovering and Loading Assets

```python
from mpfb.services.assetservice import AssetService

# Get all available clothes assets (cached)
clothes = AssetService.get_asset_list("clothes", "mhclo")
for label, info in clothes.items():
    print(f"{label}: {info['full_path']}")

# Find the absolute path of a specific asset
jeans_path = AssetService.find_asset_absolute_path(
    "jeans/jeans.mhclo", asset_subdir="clothes"
)
```

### Finding Alternative Materials

```python
from mpfb.services.assetservice import AssetService

# Find alternative materials for a clothing item
alt_materials = AssetService.alternative_materials_for_asset(
    "jeans/jeans.mhclo", asset_subdir="clothes"
)
for mat_path in alt_materials:
    print(f"Alternative material: {mat_path}")
```

### Working with Asset Packs

```python
from mpfb.services.assetservice import AssetService

# Check if system assets are installed
if AssetService.system_assets_pack_is_installed():
    print("System assets are available")

# List all packs and their contents
for pack_name in AssetService.get_pack_names():
    assets = AssetService.get_asset_names_in_pack(pack_name)
    print(f"Pack '{pack_name}': {len(assets)} assets")
```
