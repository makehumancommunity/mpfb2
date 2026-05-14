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

import os

# Equivalent of imports
HumanService = dynamic_import("mpfb.services.humanservice", "HumanService")
TargetService = dynamic_import("mpfb.services.targetservice", "TargetService")
LocationService = dynamic_import("mpfb.services.locationservice", "LocationService")

# Non-macro modeling targets (i.e. anything except race/age/gender/weight/height/muscle/proportions)
# are stored as shape keys on the basemesh. Each shape key has a value in roughly the 0.0-1.0
# range, although values outside this range are accepted and will produce exaggerated results.

# Built-in targets live under the addon's data directory. LocationService.get_mpfb_data("targets")
# returns the absolute path to that directory, regardless of where the extension was installed.
targets_root = LocationService.get_mpfb_data("targets")

# Reference human with default proportions
reference_human = HumanService.create_human()
reference_human.location = (-1, 0, 0)

# Human with a more prominent nose
big_nose_human = HumanService.create_human()
big_nose_human.location = (1, 0, 0)

# Increase overall nose volume
TargetService.load_target(
    big_nose_human,
    os.path.join(targets_root, "nose", "nose-volume-incr.target.gz"),
    weight=1.0)

# ... and make it a bit wider at the same time
TargetService.load_target(
    big_nose_human,
    os.path.join(targets_root, "nose", "nose-scale-horiz-incr.target.gz"),
    weight=0.5)
