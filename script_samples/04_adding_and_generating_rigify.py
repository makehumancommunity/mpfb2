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
SystemService = dynamic_import("mpfb.services.systemservice", "SystemService")
RigifyHelpers = dynamic_import("mpfb.entities.rigging.rigifyhelpers.rigifyhelpers", "RigifyHelpers")
GeneralObjectProperties = dynamic_import("mpfb.entities.objectproperties", "GeneralObjectProperties")

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

# bpy.ops.pose.rigify_generate() reads its input from the active object, so make sure the
# metarig is selected and active, and that we are in Object mode.
bpy.ops.object.select_all(action='DESELECT')
metarig.select_set(True)
bpy.context.view_layer.objects.active = metarig
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

# Newer rigify versions split the face rig into a separate sub-rig; upgrade if available.
if bpy.ops.pose.rigify_upgrade_face.poll():
    bpy.ops.pose.rigify_upgrade_face()

# Generate the control rig. After this call, the active object is the generated rig
# (typically named "RIG-Human.rigify").
bpy.ops.pose.rigify_generate()
rigify_object = bpy.context.active_object
rigify_object.show_in_front = True
rigify_object.parent = metarig.parent

# Re-parent the basemesh (and any sub-rigs / assets) from the metarig to the generated rig
# and remap their Armature modifiers / constraints accordingly.
RigifyHelpers.adjust_children_for_rigify(rigify_object, metarig)

# Tell MPFB that the new object is a Skeleton so downstream features (pose loading,
# export, ...) recognise it.
GeneralObjectProperties.set_value("object_type", "Skeleton", entity_reference=rigify_object)

# Remove the now-superfluous metarig.
bpy.data.objects.remove(metarig, do_unlink=True)

# Leave the generated rig as the active selection.
bpy.ops.object.select_all(action='DESELECT')
rigify_object.select_set(True)
bpy.context.view_layer.objects.active = rigify_object
