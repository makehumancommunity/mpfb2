"""Operator for making left side a mirrored copy of right side."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.targetservice import TargetService
from mpfb import ClassManager

_LOG = LogService.get_logger("maketarget.symmetrizeleft")

class MPFB_OT_SymmetrizeLeftOperator(bpy.types.Operator):
    """Symmetrize by taking the right side of the model and copy it mirrored to the left side"""
    bl_idname = "mpfb.symmetrize_maketarget_left"
    bl_label = "Copy -x to +x"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if not ObjectService.object_is_basemesh(context.active_object):
            return False
        if context.active_object.data.shape_keys:
            return True
        return False

    def execute(self, context):

        blender_object = context.active_object
        TargetService.symmetrize_shape_key(blender_object, "PrimaryTarget", False)

        self.report({'INFO'}, "Target symmetrized")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_SymmetrizeLeftOperator)
