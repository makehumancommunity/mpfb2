# Scripting MPFB

This directory contains practical examples of how to use MPFB for your own scripts.

## Creating a basic human

First steps: create a basic human mesh. 

[01_create_a_basic_human.py](01_create_a_basic_human.py)

Relevant parts of the documentation:

- [HumanService.create_human()](../docs/services/humanservice.md#character-creation)
- [TargetService.reapply_macro_details()](../docs/services/targetservice.md#reapply_macro_detailsbasemesh-remove_zero_weight_targetstrue)
- [HumanObjectProperties](../docs/entities/objectproperties.md#humanobjectproperties)

## Working with modeling targets

Example: how to make the nose larger by loading individual (non-macro) modeling targets onto a basemesh.

[02_working_with_modeling_targets.py](02_working_with_modeling_targets.py)

Relevant parts of the documentation:

- [TargetService.load_target()](../docs/services/targetservice.md#load_targetblender_object-full_path--weight00-namenone)
- [LocationService.get_mpfb_data()](../docs/services/locationservice.md#get_mpfb_datasub_pathnone)

## Adding a default rig

Example: attach one of the built-in rigs (default, mixamo, game_engine, ...) to a basemesh.

[03_adding_a_default_rig.py](03_adding_a_default_rig.py)

Relevant parts of the documentation:

- [HumanService.add_builtin_rig()](../docs/services/humanservice.md#add_builtin_rigbasemesh-rig_name--import_weightstrue-operatornone)

## Adding and generating a rigify rig

Example: attach the default rigify metarig to a basemesh and then generate it to get a rigify control rig. Requires the Rigify addon to be enabled under Preferences -> Add-ons.

[04_adding_and_generating_rigify.py](04_adding_and_generating_rigify.py)

Relevant parts of the documentation:

- [HumanService.add_builtin_rig()](../docs/services/humanservice.md#add_builtin_rigbasemesh-rig_name--import_weightstrue-operatornone) (passing a `rig_name` that starts with `rigify.` creates a metarig instead of a standard rig)
- [SystemService.check_for_rigify()](../docs/services/systemservice.md#check_for_rigify)

The actual generation step is performed by Rigify itself (`bpy.ops.pose.rigify_generate`). MPFB's `RigifyHelpers.adjust_children_for_rigify()` is then used to re-parent the basemesh from the metarig onto the generated control rig.

## Setting skin

Example: apply a skin material (.mhmat) from the `makehuman_system_assets` pack to a basemesh.

[05_setting_skin.py](05_setting_skin.py)

Note that this example assumes that the [makehuman_system_assets](https://static.makehumancommunity.org/asset_packs/makehuman_system_assets.html) asset pack has been installed.

Relevant parts of the documentation:

- [HumanService.set_character_skin()](../docs/services/humanservice.md#set_character_skinmhmat_file-basemesh-bodyproxynone-skin_typeenhanced_sss-material_instancestrue-slot_overridesnone)
- [AssetService.find_asset_absolute_path()](../docs/services/assetservice.md#find_asset_absolute_pathasset_path_fragment-asset_subdirclothes)

## Adding basic assets from the system assets pack

Example: add eyes, eyebrows, eyelashes, tongue and teeth to a basemesh.

[06_adding_basic_assets.py](06_adding_basic_assets.py)

Note that this example assumes that the [makehuman_system_assets](https://static.makehumancommunity.org/asset_packs/makehuman_system_assets.html) asset pack has been installed.

Relevant parts of the documentation:

- [HumanService.add_mhclo_asset()](../docs/services/humanservice.md#add_mhclo_assetmhclo_file-basemesh-asset_typeclothes-subdiv_levels1-material_typemakeskin-alternative_materialsnone-color_adjustmentsnone-set_up_riggingtrue-interpolate_weightstrue-import_subrigtrue-import_weightstrue)
- [AssetService.find_asset_absolute_path()](../docs/services/assetservice.md#find_asset_absolute_pathasset_path_fragment-asset_subdirclothes)

## Getting a list of installed asset packs

Example: getting a list of installed asset packs, plus how many assets each pack declares.

[07_listing_asset_packs.py](07_listing_asset_packs.py)

Relevant parts of the documentation:

- [AssetService.rescan_pack_metadata()](../docs/services/assetservice.md#rescan_pack_metadata)
- [AssetService.have_any_pack_meta_data()](../docs/services/assetservice.md#have_any_pack_meta_data)
- [AssetService.get_pack_names()](../docs/services/assetservice.md#get_pack_names)
- [AssetService.get_asset_names_in_pack()](../docs/services/assetservice.md#get_asset_names_in_packpack_name)

## Getting information about installed assets

Example: Using AssetService to get a complete list of all installed clothes assets. The same pattern works for any other asset subdir (`eyes`, `hair`, `eyebrows`, `eyelashes`, `tongue`, `teeth`, `proxymeshes`, or `skins` with `asset_type="mhmat"`).

[08_listing_installed_clothes.py](08_listing_installed_clothes.py)

Relevant parts of the documentation:

- [AssetService.update_asset_list()](../docs/services/assetservice.md#update_asset_listasset_subdirclothes-asset_typemhclo)
- [AssetService.get_asset_list()](../docs/services/assetservice.md#get_asset_listasset_subdirclothes-asset_typemhclo)

## Getting information about bundled targets

Example: Iterating over `data/targets/target.json` to get a list of all bundled non-macro targets. Note that there is no dedicated TargetService API for enumerating bundled targets &mdash; use the JSON for discovery and [TargetService.load_target()](../docs/services/targetservice.md#load_targetblender_object-full_path--weight00-namenone) / [TargetService.target_full_path()](../docs/services/targetservice.md#target_full_pathtarget_name) to actually load one.

[09_listing_bundled_targets.py](09_listing_bundled_targets.py)

Relevant parts of the documentation:

- [LocationService.get_mpfb_data()](../docs/services/locationservice.md#get_mpfb_datasub_pathnone)

## Creating a complete character and exporting it to FBX

Example: Create a complete character with eyes, eyebrows, eyelashes, tongue, teeth, hair and a set of clothes, using GameEngine for all materials. The character is then staged through `ExportService` (which duplicates the hierarchy, bakes modifiers and strips helper geometry) and exported to FBX.

[10_complete_character_export_fbx.py](10_complete_character_export_fbx.py)

Note that this example assumes that the [makehuman_system_assets](https://static.makehumancommunity.org/asset_packs/makehuman_system_assets.html) asset pack has been installed.

Relevant parts of the documentation:

- [HumanService.set_character_skin()](../docs/services/humanservice.md#set_character_skinmhmat_file-basemesh-bodyproxynone-skin_typeenhanced_sss-material_instancestrue-slot_overridesnone)
- [HumanService.add_mhclo_asset()](../docs/services/humanservice.md#add_mhclo_assetmhclo_file-basemesh-asset_typeclothes-subdiv_levels1-material_typemakeskin-alternative_materialsnone-color_adjustmentsnone-set_up_riggingtrue-interpolate_weightstrue-import_subrigtrue-import_weightstrue)
- [HumanService.add_builtin_rig()](../docs/services/humanservice.md#add_builtin_rigbasemesh-rig_name--import_weightstrue-operatornone)
- [ExportService.create_character_copy()](../docs/services/exportservice.md#create_character_copysource_object-name_suffix_export_copy-place_in_collectionnone)
- [ExportService.bake_modifiers_remove_helpers()](../docs/services/exportservice.md#bake_modifiers_remove_helpersbasemesh-bake_masksfalse-bake_subdivfalse-remove_helperstrue-also_proxytrue)

