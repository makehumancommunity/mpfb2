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

# AssetService maintains a cached, label-keyed dict of every .mhclo it found under each
# configured asset root's "clothes" subdir. Force a refresh first so the listing reflects
# the current state of the filesystem.
AssetService.update_asset_list(asset_subdir="clothes", asset_type="mhclo")
clothes = AssetService.get_asset_list(asset_subdir="clothes", asset_type="mhclo")

# The same pattern works for any other asset_subdir, e.g. "eyes", "hair", "eyebrows",
# "eyelashes", "tongue", "teeth", "proxymeshes" or "skins" (with asset_type="mhmat").

print(f"Found {len(clothes)} installed clothes asset(s):")
for label in sorted(clothes.keys()):
    item = clothes[label]
    # Each entry holds the resolved label, the bare filename, and the absolute path.
    print(f"  - {item['label']}")
    print(f"      basename:  {item['basename']}")
    print(f"      full_path: {item['full_path']}")
