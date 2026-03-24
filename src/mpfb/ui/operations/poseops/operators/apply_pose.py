"""Operator for applying a pose as rest pose and handle the consequences for child meshes."""

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from .....entities.material.makeskinmaterial import MakeSkinMaterial
from .....services import LogService
from .....services import ObjectService
from .....services import RigService
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy

_LOG = LogService.get_logger("poseops.apply_pose")

@pollstrategy(PollStrategy.RIG_ACTIVE)
class MPFB_OT_Apply_Pose_Operator(bpy.types.Operator):
    """Apply pose as rest pose. WARNING: This will also bake all shape keys and make it impossible to do further modeling"""
    bl_idname = "mpfb.apply_pose"
    bl_label = "Apply as rest pose"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        scn = context.scene

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        RigService.apply_pose_as_rest_pose(obj)

        self.report({'INFO'}, "Pose applies")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Apply_Pose_Operator)
