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

# The built-in rigs that ship with MPFB live under src/mpfb/data/rigs/standard/ and can be
# referenced by name. Available standard rigs:
#
#   "default"                  - the canonical MakeHuman rig
#   "default_no_toes"          - same as default, but without individual toe bones
#   "cmu_mb"                   - CMU motion capture compatible
#   "game_engine"              - simplified rig suitable for game engines
#   "game_engine_with_breast"  - game engine rig with extra breast bones
#   "mixamo"                   - compatible with Adobe Mixamo
#   "mixamo_unity"             - Mixamo variant tuned for Unity
#   "openpose"                 - matches the OpenPose keypoint topology
#
# Passing a rig_name that starts with "rigify." (e.g. "rigify.default") will create a Rigify
# metarig instead. That path requires the Rigify addon to be enabled in Blender.

basemesh = HumanService.create_human()

rig = HumanService.add_builtin_rig(basemesh, "default")
