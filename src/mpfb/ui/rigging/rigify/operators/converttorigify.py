from .....services import LogService
from .....services import ObjectService
from .....services import RigService
from ..... import ClassManager
from .....entities.rigging.rigifyhelpers.rigifyhelpers import RigifyHelpers
from .....services import SystemService
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator
import bpy, json

_LOG = LogService.get_logger("rigify.operators.converttorigify")


@pollstrategy(PollStrategy.RIG_ACTIVE)
class MPFB_OT_Convert_To_Rigify_Operator(MpfbOperator):
    """Convert rig to rigify"""
    bl_idname = "mpfb.convert_to_rigify"
    bl_label = "Rigify"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
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

        from ...rigify.rigifypanel import RIGIFY_PROPERTIES
        settings = RIGIFY_PROPERTIES.as_dict(entity_reference=context.scene)

        helpers = RigifyHelpers.get_instance(settings)
        helpers.convert_to_rigify(blender_object)

        self.report({'INFO'}, "Converted to rigify")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Convert_To_Rigify_Operator)
