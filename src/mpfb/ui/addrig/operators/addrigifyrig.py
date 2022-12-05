"""Operator for adding a rigify rig."""

import bpy, os, json
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.locationservice import LocationService
from mpfb.services.rigifyhelpers.rigifyhelpers import RigifyHelpers
from mpfb.services.rigservice import RigService
from mpfb.entities.rig import Rig
from mpfb.services.systemservice import SystemService
from mpfb import ClassManager

_LOG = LogService.get_logger("addrig.add_rigify_rig")

class MPFB_OT_AddRigifyRigOperator(bpy.types.Operator):
    """Add a rigify rig"""

    bl_idname = "mpfb.add_rigify_rig"
    bl_label = "Add rigify rig"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            return ObjectService.object_is_basemesh(context.active_object)
        return False

    def execute(self, context):

        if not SystemService.check_for_rigify():
            self.report({'ERROR'}, "The rigify addon isn't enabled. You need to enable it under preferences.")
            return {'FINISHED'}

        scene = context.scene

        if not ObjectService.object_is_basemesh(context.active_object):
            self.report({'ERROR'}, "Rigs can only be added to the base mesh")
            return {'FINISHED'}

        basemesh = context.active_object

        from mpfb.ui.addrig.addrigpanel import ADD_RIG_PROPERTIES # pylint: disable=C0415

        rigify_rig = ADD_RIG_PROPERTIES.get_value("rigify_rig", entity_reference=scene)
        import_weights = ADD_RIG_PROPERTIES.get_value("import_weights_rigify", entity_reference=scene)
        delete_after_generate = ADD_RIG_PROPERTIES.get_value("delete_after_generate", entity_reference=scene)

        rigs_dir = LocationService.get_mpfb_data("rigs")
        rigify_dir = os.path.join(rigs_dir, "rigify")

        rig_file = os.path.join(rigify_dir, "rig." + rigify_rig + ".json")

        rig = Rig.from_json_file_and_basemesh(rig_file, basemesh)
        armature_object = rig.create_armature_and_fit_to_basemesh()

        assert len(armature_object.data.rigify_layers) > 0

        armature_object.name = armature_object.data.name = basemesh.name + ".metarig"

        if hasattr(armature_object.data, 'rigify_rig_basename'):
            armature_object.data.rigify_rig_basename = "Human.rigify"

        basemesh.parent = armature_object

        if import_weights:
            for try_rig in RigService.get_rig_weight_fallbacks("rigify." + rigify_rig):
                try_rig = try_rig.replace("rigify.", "")
                weights_file = os.path.join(rigify_dir, "weights." + try_rig + ".json")

                if os.path.isfile(weights_file):
                    break
            else:
                self.report({'ERROR'}, "Could not find the weights file")
                return {'FINISHED'}

            RigService.load_weights(armature_object, basemesh, weights_file)
            RigService.ensure_armature_modifier(basemesh, armature_object)

        self.report({'INFO'}, "A rig was added")
        return {'FINISHED'}



ClassManager.add_class(MPFB_OT_AddRigifyRigOperator)

