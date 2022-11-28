"""Operator for adding a standard rig."""

import bpy, os, json
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.locationservice import LocationService
from mpfb.services.rigservice import RigService
from mpfb.entities.rig import Rig
from mpfb import ClassManager

_LOG = LogService.get_logger("addrig.add_standard_rig")

class MPFB_OT_AddStandardRigOperator(bpy.types.Operator):
    """Add a standard (non-rigify) rig"""

    bl_idname = "mpfb.add_standard_rig"
    bl_label = "Add standard rig"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            return ObjectService.object_is_basemesh(context.active_object)
        return False

    def execute(self, context):
        scene = context.scene

        if not ObjectService.object_is_basemesh(context.active_object):
            self.report({'ERROR'}, "Rigs can only be added to the base mesh")
            return {'FINISHED'}

        basemesh = context.active_object

        from mpfb.ui.addrig.addrigpanel import ADD_RIG_PROPERTIES # pylint: disable=C0415

        import_weights = ADD_RIG_PROPERTIES.get_value("import_weights", entity_reference=scene)
        standard_rig = ADD_RIG_PROPERTIES.get_value("standard_rig", entity_reference=scene)

        rigs_dir = LocationService.get_mpfb_data("rigs")
        standard_dir = os.path.join(rigs_dir, "standard")

        rig_file = os.path.join(standard_dir, "rig." + standard_rig + ".json")

        rig = Rig.from_json_file_and_basemesh(rig_file, basemesh)
        armature_object = rig.create_armature_and_fit_to_basemesh()

        basemesh.parent = armature_object

        if import_weights:
            weights_file = os.path.join(standard_dir, "weights." + standard_rig + ".json")
            RigService.load_weights(armature_object, basemesh, weights_file)
            RigService.ensure_armature_modifier(basemesh, armature_object)

        RigService.normalize_rotation_mode(armature_object)

        self.report({'INFO'}, "A rig was added")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_AddStandardRigOperator)

