# Apply Assets — "Load MHCLO"

**Source:** `src/mpfb/ui/apply_assets/loadclothes/`

**Parent panel:** `MPFB_PT_Assets_Panel` ("Apply assets")

## Overview

The "Load MHCLO" panel provides a more direct alternative to the asset library. Instead of browsing a pre-scanned library grid, the user selects any `.mhclo` file from anywhere on the filesystem using a standard Blender file browser. This is useful when working with assets that are not installed in the user data directory, such as when testing a newly created clothing file before installing it properly.

The panel reads the same set of fitting, material, rigging, and subdivision settings from `ASSET_SETTINGS_PROPERTIES` (the `ASLS_` properties defined in `assetlibrary/assetsettingspanel.py`) as all the library panels, so the loading behaviour is consistent. The only extra thing the user must specify is the object type — because the file browser provides no metadata, MPFB cannot determine whether the asset is clothes, eyes, a proxy mesh, or something else automatically.

## Panel

### MPFB_PT_Load_Clothes_Panel ("Load MHCLO")

| Attribute | Value |
|---|---|
| `bl_label` | `"Load MHCLO"` |
| `bl_category` | `CLOTHESCATEGORY` |
| `bl_parent_id` | `"MPFB_PT_Assets_Panel"` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"LC_"` |

Draws the `object_type` dropdown so the user can specify what kind of asset they are loading (Clothes, Proxymeshes, Eyes, Eyebrows, Eyelashes, Teeth, or Tongue), then a "Load clothes from file" button that opens the file browser.

## Operator

### MPFB_OT_Load_Clothes_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_clothes` |
| `bl_label` | `"Load clothes from file"` |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Base class | `bpy.types.Operator`, `ImportHelper` |
| File filter | `*.mhclo` |

**Note:** This operator inherits directly from `bpy.types.Operator` and `ImportHelper` rather than from `MpfbOperator`. This means it does not use `MpfbOperator`'s `hardened_execute()` error-handling wrapper.

The operator has two code paths, chosen at runtime based on whether a basemesh is available and `fit_to_body` is enabled.

**Path A — integrated path (basemesh present and `fit_to_body` enabled):**

1. Validates that all enabled prerequisites are met: basemesh required for `fit_to_body`, `delete_group`, and `interpolate_weights`; rig required for `set_up_rigging`. Reports an error and returns early if any precondition fails.
2. Delegates entirely to `HumanService.add_mhclo_asset()`, passing the file path, basemesh, object type, material type (`"MAKESKIN"`), rigging and weight options, and subdivision level.

**Path B — manual path (no basemesh, or `fit_to_body` disabled):**

1. Loads the MHCLO file using the `Mhclo` entity and calls `mhclo.load_mesh()` to create the Blender mesh object.
2. Sets the `object_type` property on the new object via `GeneralObjectProperties`.
3. Applies smooth shading with `bpy.ops.object.shade_smooth()`.
4. If `material_type` is `"MAKESKIN"` and the MHCLO references a material file, creates a MakeSkin material and applies it to the object.
5. If `fit_to_body`: calls `ClothesService.fit_clothes_to_human()` and `mhclo.set_scalings()` to deform the mesh to match the character.
6. If `delete_group`: calls `ClothesService.update_delete_group()` to update the basemesh's delete group. If `specific_delete_group` is also enabled, the delete group is named after the MHCLO filename (in the form `Delete.<filename>`) rather than the generic `"Delete"`.
7. If `set_up_rigging`: moves the clothes mesh to the world origin and calls `ClothesService.set_up_rigging()` to parent it to the rig and set up vertex weights. Otherwise, parents the clothes to the basemesh if one is available.
8. If `makeclothes_metadata`: calls `ClothesService.set_makeclothes_object_properties_from_mhclo()` to store MakeClothes-specific metadata on the object.

## Properties

### LC_ — load clothes properties

Loaded from JSON files in `src/mpfb/ui/apply_assets/loadclothes/properties/` with prefix `"LC_"`.

| Property | Type | Default | Description |
|---|---|---|---|
| `object_type` | enum | `"Clothes"` | The sub-type to assign the loaded mesh: `Clothes`, `Proxymeshes`, `Eyes`, `Eyebrows`, `Eyelashes`, `Teeth`, or `Tongue` |

All other settings that affect loading (fitting, rigging, materials, subdivision) are read from `ASSET_SETTINGS_PROPERTIES` (prefix `"ASLS_"`), which is shared with the library panels. See [assetlibrary.md](assetlibrary.md) for a full description of those properties.

## Related

- [HumanService](../../services/humanservice.md) — provides `add_mhclo_asset()`
- [ClothesService](../../services/clothesservice.md) — provides `fit_clothes_to_human()`, `set_up_rigging()`, and `update_delete_group()`
- [Asset library](assetlibrary.md) — the library-based interface for loading the same types of assets
- [MHCLO file format](../../fileformats/mhclo.md) — the `.mhclo` format used for clothes and body-part assets
