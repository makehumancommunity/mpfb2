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
HumanService = dynamic_import("mpfb.services.humanservice", "HumanService")
AssetService = dynamic_import("mpfb.services.assetservice", "AssetService")

# This example assumes the "makehuman_system_assets" asset pack has been installed,
# as it provides the "young_caucasian_female" skin. See
# https://static.makehumancommunity.org/asset_packs/makehuman_system_assets.html

basemesh = HumanService.create_human()

# AssetService.find_asset_absolute_path() walks the configured asset roots looking for the
# requested filename under the given asset_subdir. It returns None if nothing was found.
mhmat_path = AssetService.find_asset_absolute_path("young_caucasian_female.mhmat", asset_subdir="skins")

if mhmat_path is None:
    raise RuntimeError(
        "Could not find young_caucasian_female.mhmat. "
        "Install the makehuman_system_assets pack and configure the assets directory in MPFB preferences.")

# Valid skin_type values are "ENHANCED_SSS" (default), "MAKESKIN", "GAMEENGINE" and "LAYERED".
# MAKESKIN produces a single, easy-to-inspect node tree that is closest to the raw .mhmat file
# and works the same across all renderers.
HumanService.set_character_skin(mhmat_path, basemesh, skin_type="MAKESKIN")
