# ------------------------------------------------------------------------------------------
# This quirk needs to be copy/pasted into every script. Blender extensions end up
# on unknown places in the module hierarchy, so at write time you don't know the
# absolute package name. Thus we iterate over all modules known by sys to find
# a package and a the key of a declared symbol
#
import importlib, sys
def dynamic_import(absolute_package_str, key):
    """Quirk to get around blender's extension format's requirement that all imports must be relative"""
    for amod in sys.modules:
        if amod.endswith(absolute_package_str):
            mpfb_mod = importlib.import_module(amod)
            if not hasattr(mpfb_mod, key):
                raise AttributeError(f"Module {amod} does not have attribute {key}")
            return getattr(mpfb_mod, key)
    raise ValueError(f"No module found with name ending in {absolute_package_str}")
#
# ------------------------------------------------------------------------------------------

# Equivalent of imports
AssetService = dynamic_import("mpfb.services.assetservice", "AssetService")

# Asset packs are described by .json files dropped into the user data "packs" directory by
# the pack installers. Force a fresh scan in case nothing has touched the cache yet in this
# Blender session.
AssetService.rescan_pack_metadata()

if not AssetService.have_any_pack_meta_data():
    print("No asset packs are installed. See https://static.makehumancommunity.org/asset_packs/ for available packs.")
else:
    pack_names = AssetService.get_pack_names()
    print(f"Found {len(pack_names)} installed asset pack(s):")
    for pack_name in pack_names:
        # get_asset_names_in_pack returns a sorted list of asset keys declared in the pack json.
        asset_names = AssetService.get_asset_names_in_pack(pack_name)
        print(f"  - {pack_name} ({len(asset_names)} assets)")
