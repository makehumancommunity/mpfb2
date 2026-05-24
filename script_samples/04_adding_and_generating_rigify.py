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

import bpy

# Equivalent of imports
HumanService = dynamic_import("mpfb.services.humanservice", "HumanService")
RigService = dynamic_import("mpfb.services.rigservice", "RigService")
SystemService = dynamic_import("mpfb.services.systemservice", "SystemService")

# Rigify is shipped with Blender but must be enabled under Preferences -> Add-ons.
# Bail out cleanly if it isn't available rather than trace-backing inside rigify_generate().
if not SystemService.check_for_rigify():
    raise RuntimeError("The rigify addon isn't enabled. Enable it under Preferences -> Add-ons before running this script.")

# Create a basemesh, then attach the rigify metarig. The available rigify presets shipped
# with MPFB live under src/mpfb/data/rigs/rigify/ and are:
#
#   "rigify.human"       - the canonical metarig
#   "rigify.human_toes"  - same metarig but with individual toe bones
#
# add_builtin_rig() handles the "rigify." prefix internally: it loads the matching JSON,
# fits the metarig to the basemesh, parents the basemesh to the armature, names the armature
# "<basemesh>.metarig" and sets rigify_rig_basename to "Human.rigify".
basemesh = HumanService.create_human()
metarig = HumanService.add_builtin_rig(basemesh, "rigify.human")

# Generate the full rigify rig. RigService.generate_rigify_rig handles everything that
# the UI operator does: selecting the meta rig, optionally upgrading the face rig,
# validating with rigify.utils.rig.is_valid_metarig, running pose.rigify_generate,
# re-parenting the new rig, calling RigifyHelpers.adjust_children_for_rigify, copying
# object_type onto the rigify rig, and applying the chosen meta_rig_action
# ("keep" / "hide" / "delete"; default is "hide").
rigify_object = RigService.generate_rigify_rig(metarig, meta_rig_action="delete")

# Leave the generated rig as the active selection.
bpy.ops.object.select_all(action='DESELECT')
rigify_object.select_set(True)
bpy.context.view_layer.objects.active = rigify_object
