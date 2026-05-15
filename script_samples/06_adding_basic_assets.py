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

# This example assumes the "makehuman_system_assets" asset pack has been installed.
# See https://static.makehumancommunity.org/asset_packs/makehuman_system_assets.html
#
# Eyes, eyebrows, eyelashes, tongue and teeth all use the .mhclo format, so they are loaded
# via HumanService.add_mhclo_asset(). The asset_type argument is important: it is stored on
# the resulting object and drives how MPFB treats the asset later (refit, grouping, etc.).

basemesh = HumanService.create_human()

# (subdir under the assets root, .mhclo filename, asset_type to assign)
assets = [
    ("eyes",      "low-poly.mhclo",    "Eyes"),
    ("eyebrows",  "eyebrow001.mhclo",  "Eyebrows"),
    ("eyelashes", "eyelashes01.mhclo", "Eyelashes"),
    ("tongue",    "tongue01.mhclo",    "Tongue"),
    ("teeth",     "teeth_base.mhclo",  "Teeth"),
]

for subdir, fname, atype in assets:
    path = AssetService.find_asset_absolute_path(fname, asset_subdir=subdir)
    if path is None:
        print(f"Skipping {atype}: {fname} not found (makehuman_system_assets pack required)")
        continue
    HumanService.add_mhclo_asset(path, basemesh, asset_type=atype)
