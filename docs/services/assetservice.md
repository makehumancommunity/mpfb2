# AssetService

## Overview

AssetService manages the discovery, cataloging, and caching of MPFB asset files across multiple data root directories. It provides the primary interface for locating assets (clothes, skins, eyes, hair, poses, etc.) stored on disk and for managing asset pack metadata.

MPFB assets are organized in a hierarchy of data roots: the built-in MPFB data directory, the MakeHuman user directory, the MPFB user directory, and an optional secondary root. Within each root, assets are grouped by subdirectory (e.g., `clothes`, `skins`, `eyes`, `poses`). AssetService scans these locations, resolves file paths, and maintains a cached dictionary of discovered assets with their metadata and thumbnail previews.

The service also manages **asset packs** — bundles of assets distributed as downloadable packages. Pack metadata is stored as JSON files in the user's `packs` directory and can be queried to determine which assets are installed and available.

In addition, AssetService is responsible for discovering **custom rigs** stored in the `rigs/` subdirectory of user data roots. Custom rigs are JSON files whose names consist only of alphanumeric characters and underscores and which contain an `"identifying_bones"` key. The results are cached in a module-level variable and can be invalidated when a new rig is saved to the library. All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/assetservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.assetservice")` |
| `LocationService` | Resolving data roots (user data, MakeHuman data, MPFB data, secondary root) |
| `SystemService` | Path segment matching for alternative material discovery |

## Module-Level State

In addition to `ASSET_LIBRARY_SECTIONS` and the asset list cache, the module maintains:

- `_ASSETS: dict[str, dict[str, dict[str, Any]]]` — The asset list cache, keyed on asset subdir and then on asset label. Populated by `update_asset_list()` and read by `get_asset_list()`.
- `_ASSET_THUMBS: ImagePreviewCollection | None` — The single `bpy.utils.previews` collection every asset and material thumbnail is loaded into. `None` until the first thumbnail is loaded.
- `_CUSTOM_RIGS_CACHE: list[dict[str, Any]] | None` — A cached list of custom rig dictionaries discovered in user data roots. Initially `None`; populated on the first call to `get_custom_rigs()` and cleared by `invalidate_custom_rig_cache()`.
- `_ALTERNATIVE_MATERIALS: dict[tuple[str, str], list[str]]` — Alternative material paths, keyed on `(asset_source, asset_subdir)`. Populated on the first call to `alternative_materials_for_asset()` for a given asset and cleared by `invalidate_alternative_materials_cache()`.
- `_ALTERNATIVE_MATERIAL_TILES: dict[tuple[str, str], list[dict[str, Any]]]` — The same, but for the UI items produced by `alternative_material_tiles_for_asset()`.
- `_PACKS: dict[str, dict[str, Any]] | None` — Pack name to that pack's JSON contents, which map asset name to the asset's metadata. `None` means "not yet scanned", which is the state `_ensure_pack_metadata()` tests; an empty dict means "scanned, and there are no packs".

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
| `ink_overrides` | `bool` | Whether the section supports ink layer overrides. Present on the Ink layers section only, so callers must use `section.get("ink_overrides", False)` rather than subscripting |

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

**Returns:** `str | None` — The absolute path to the asset, or `None` if not found.

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

The result is deduplicated and sorted, and is cached per asset source. An asset source which cannot be resolved gives an empty list. Note that `exclude_default` is not currently implemented, and the default material is thus always included if it resides in the searched directories.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_source` | `str \| None` | — | The source path fragment of the asset |
| `asset_subdir` | `str` | `"clothes"` | The asset subdirectory to search within |
| `exclude_default` | `bool` | `True` | Not implemented |

**Returns:** `list[str]` — Sorted list of absolute paths to alternative material files.

---

#### alternative_material_tiles_for_asset(asset_source, asset_subdir="clothes")

Find alternative materials for an asset, with thumbnails and labels suitable for drawing a UI grid. Builds on `alternative_materials_for_asset()`, and is likewise cached per asset source.

The returned items have the same shape as those in the asset list, see `update_asset_list()`. Thumbnails are read from a `<basename>.thumb` file next to the `.mhmat` file, and are loaded into the same preview collection as the asset list uses. Materials without a thumbnail of their own get the bundled placeholder, so that all tiles can be drawn at the same size.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_source` | `str \| None` | — | The source path fragment of the asset |
| `asset_subdir` | `str` | `"clothes"` | The asset subdirectory to search within |

**Returns:** `list[dict[str, Any]]` — List of items describing the alternative materials.

---

#### get_placeholder_thumbnail()

Get the preview for the bundled placeholder image (`data/textures/notfound.thumb`), to be used for assets which do not have a thumbnail of their own.

**Returns:** `Any` — The `bpy.types.ImagePreview` for the placeholder, or `None` if the bundled image is
missing. Annotated `Any` rather than `ImagePreview | None` because the value is handed straight to a
`UILayout`'s `icon_value`, and the preview collection is a `dict` subclass whose element type the stubs
only describe loosely.

---

#### invalidate_alternative_materials_cache()

Empty the cache of alternative materials, so that it is rescanned on next request. Called by `update_all_asset_lists()`.

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

Update the global asset list cache for all sections defined in `ASSET_LIBRARY_SECTIONS`. Also invalidates both the alternative materials cache and the pack metadata cache.

**Returns:** None

---

#### get_asset_list(asset_subdir="clothes", asset_type="mhclo")

Retrieve the cached asset list for a subdirectory and type. If the list is not yet cached, it is built automatically by calling `update_asset_list`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_subdir` | `str` | `"clothes"` | The subdirectory to retrieve |
| `asset_type` | `str` | `"mhclo"` | The file extension type |

**Returns:** `dict[str, dict[str, Any]]` — Dictionary mapping asset labels to asset info dictionaries.

---

#### path_to_fragment(asset_full_path, relative_to_fragment=None, asset_subdir="clothes")

Convert an absolute asset path to a relative fragment of the form `parent_dir/filename`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `asset_full_path` | `str` | — | The absolute path to convert |
| `relative_to_fragment` | `str \| None` | `None` | Reserved for future use |
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

#### invalidate_pack_metadata_cache()

Empty the cache of pack metadata, so that it is rescanned on the next request. Called by `update_all_asset_lists()`.

**Returns:** None

---

#### rescan_pack_metadata()

Reload all asset pack metadata from JSON files in the user's `packs` directory. This always performs a fresh scan, replacing any previously cached metadata.

**Returns:** None

Note that a scan which finds no packs at all still counts as having been scanned, so neither this method nor `get_pack_names()` will hit the file system again until `invalidate_pack_metadata_cache()` has been called.

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

### Custom Rig Discovery

#### get_custom_rigs(use_cache=True)

Scan the `rigs/` subdirectory of all user data roots for custom rig JSON files. A file is included only if its name (without the `.json` extension) consists entirely of alphanumeric characters and underscores (`[a-zA-Z0-9_]+`) and if the JSON contains an `"identifying_bones"` key. The system asset root is intentionally excluded from this scan.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `use_cache` | `bool` | `True` | If `True`, return the cached list when available instead of rescanning disk |

**Returns:** `list[dict[str, Any]]` — Each dict has keys `"name"` (str, bare filename without extension), `"path"` (str, absolute path to the JSON file), and `"identifying_bones"` (list of bone name strings).

---

#### invalidate_custom_rig_cache()

Clear the cached custom rig list so that the next call to `get_custom_rigs()` performs a fresh scan of disk. Should be called whenever a new custom rig is saved to the user library.

**Returns:** None

---

#### get_custom_rigs_enum_items()

Return the list of discovered custom rigs as Blender `EnumProperty` item tuples, suitable for use in a dynamic enum callback. If no custom rigs are found, returns a single placeholder entry.

**Returns:** `list[tuple[str, str, str]]` — List of `(identifier, label, description)` tuples. When no rigs exist, returns `[("NONE", "No custom rigs found", "")]`. Otherwise each entry is `(name, "Custom: " + name, "")`.

---

### Asset Pack Installation

#### check_asset_pack_zip(filename)

Check whether a file is a valid zip containing a MakeHuman asset pack. A valid pack has `packs/` at the
root of the archive. When it does not, the method tries to tell a fixable re-packaging mistake (a single
extra root directory, typically from Safari auto-unpacking an archive the user then re-zipped) from a zip
which is simply not an asset pack.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filename` | `str` | — | The file to check |

**Returns:** `str | None` — `None` if the zip is a valid asset pack, otherwise a short code describing
what is wrong:

| Code | Meaning |
|------|---------|
| `"MACOS"` | One extra root directory, plus `__MACOSX` metadata. Fixable by `fix_and_extract_asset_pack_zip()` |
| `"STRUCTURE"` | One extra root directory, no `__MACOSX`. Also fixable |
| `"NO_PACKS"` | No `packs/` directory anywhere the method looks. Not an asset pack |
| `"INVALID_ZIP: <reason>"` | The file could not be read as a zip at all |

Note that the codes are returned, not raised, and that `None` is the success value — the sense is inverted
relative to a predicate, so test `is None` rather than truthiness.

---

#### fix_and_extract_asset_pack_zip(filename, target_dir)

Extract an asset pack zip into `target_dir`, stripping one extra root directory when the archive has one
and always stripping `__MACOSX` metadata. This is the repair path for the `"MACOS"` and `"STRUCTURE"` codes
returned by `check_asset_pack_zip()`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filename` | `str` | — | Path to the zip file |
| `target_dir` | `str` | — | Destination directory, normally the user data dir |

**Returns:** `str | None` — `None` on success, otherwise an error code: `"FIX_FAILED"` when the archive
still does not yield a `packs/` directory after stripping one root level, or `"FIX_ERROR: <reason>"` when
extraction or copying raised. As with `check_asset_pack_zip()`, `None` means success.

Extraction goes via a temporary directory, which is removed again whether or not the method succeeds.
Existing directories in `target_dir` are merged into rather than replaced (`dirs_exist_ok=True`), so
installing a pack over an older copy of itself overwrites file by file.

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

### Working with Custom Rigs

```python
from mpfb.services.assetservice import AssetService

# List all custom rigs available in user data
for rig in AssetService.get_custom_rigs():
    print(f"Custom rig: {rig['name']}, path: {rig['path']}")
    print(f"  Identifying bones: {rig['identifying_bones']}")

# Get enum items for use in a Blender EnumProperty callback
def rig_enum_items(self, context):
    return AssetService.get_custom_rigs_enum_items()

# Invalidate the cache after saving a new rig
AssetService.invalidate_custom_rig_cache()
```
