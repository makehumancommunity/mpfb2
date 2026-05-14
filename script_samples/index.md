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

## Setting skin

Example: apply a skin material (.mhmat) from the `makehuman_system_assets` pack to a basemesh.

[04_setting_skin.py](04_setting_skin.py)

Note that this example assumes that the [makehuman_system_assets](https://static.makehumancommunity.org/asset_packs/makehuman_system_assets.html) asset pack has been installed.

Relevant parts of the documentation:

- [HumanService.set_character_skin()](../docs/services/humanservice.md#set_character_skinmhmat_file-basemesh-bodyproxynone-skin_typeenhanced_sss-material_instancestrue-slot_overridesnone)
- [AssetService.find_asset_absolute_path()](../docs/services/assetservice.md#find_asset_absolute_pathasset_path_fragment-asset_subdirclothes)

## Adding basic assets from the system assets pack

Example: add eyes, eyebrows, eyelashes, tongue and teeth to a basemesh.

[05_adding_basic_assets.py](05_adding_basic_assets.py)

Note that this example assumes that the [makehuman_system_assets](https://static.makehumancommunity.org/asset_packs/makehuman_system_assets.html) asset pack has been installed.

Relevant parts of the documentation:

- [HumanService.add_mhclo_asset()](../docs/services/humanservice.md#add_mhclo_assetmhclo_file-basemesh-asset_typeclothes-subdiv_levels1-material_typemakeskin-alternative_materialsnone-color_adjustmentsnone-set_up_riggingtrue-interpolate_weightstrue-import_subrigtrue-import_weightstrue)
- [AssetService.find_asset_absolute_path()](../docs/services/assetservice.md#find_asset_absolute_pathasset_path_fragment-asset_subdirclothes)

