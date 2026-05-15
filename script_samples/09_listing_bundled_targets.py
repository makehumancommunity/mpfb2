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

import json, os

# Equivalent of imports
LocationService = dynamic_import("mpfb.services.locationservice", "LocationService")

# The bundled (non-macro) modeling targets are catalogued in data/targets/target.json.
# There is no dedicated enumeration API in TargetService; use this JSON for discovery
# and TargetService.load_target() / TargetService.target_full_path() to actually load
# one of the listed targets.
target_json_path = os.path.join(LocationService.get_mpfb_data("targets"), "target.json")

with open(target_json_path, "r") as f:
    target_metadata = json.load(f)

# Structure: { section: { "categories": [ { "name": ..., "targets": [ ... ] } ] } }
total = 0
for section in sorted(target_metadata.keys()):
    categories = target_metadata[section].get("categories", [])
    print(f"[{section}] ({len(categories)} categor{'y' if len(categories) == 1 else 'ies'})")
    for category in categories:
        targets = category.get("targets", [])
        print(f"  {category['name']}:")
        for target_name in targets:
            print(f"    - {target_name}")
            total += 1

print(f"\nTotal: {total} bundled non-macro targets listed in target.json")
