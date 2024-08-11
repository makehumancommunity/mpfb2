from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.rigservice import RigService
from mpfb._classmanager import ClassManager
from mpfb.entities.rigging.rigifyhelpers.rigifyhelpers import RigifyHelpers
from mpfb.services.systemservice import SystemService
import bpy, json

_LOG = LogService.get_logger("rigify.operators.converttorigify")


class MPFB_OT_Convert_To_Rigify_Operator(bpy.types.Operator):
    """Convert rig to rigify"""
    bl_idname = "mpfb.convert_to_rigify"
    bl_label = "Rigify"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if not ObjectService.object_is_skeleton(context.active_object):
            return False
        return True

    def execute(self, context):
        _LOG.enter()
        _LOG.debug("click")

        if not SystemService.check_for_rigify():
            self.report({'ERROR'}, "The rigify addon isn't enabled. You need to enable it under preferences.")
            return {'FINISHED'}

        blender_object = context.active_object

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        ball_r = RigService.find_edit_bone_by_name("ball_r", blender_object)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        if not ball_r:
            self.report({'ERROR'}, "Only the \"Game engine\" skeleton is supported so far")
            return {'FINISHED'}

        bpy.ops.object.transform_apply(location=True, scale=False, rotation=False)

        from mpfb.ui.rigify.rigifypanel import RIGIFY_PROPERTIES
        settings = RIGIFY_PROPERTIES.as_dict(entity_reference=context.scene)

        helpers = RigifyHelpers.get_instance(settings)
        helpers.convert_to_rigify(blender_object)

        self.report({'INFO'}, "Converted to rigify")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Convert_To_Rigify_Operator)
