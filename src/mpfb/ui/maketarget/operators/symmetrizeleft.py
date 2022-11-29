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
        blender_object = context.active_object
        if blender_object is None:
            _LOG.trace("Blender object is None")
            return False

        object_type = ObjectService.get_object_type(blender_object)

        if object_type != "Basemesh":
            _LOG.trace("Wrong object type", object_type)
            return False

        if not context.active_object.data.shape_keys:
            _LOG.trace("No shape keys", object_type)

        return TargetService.has_target(blender_object, "PrimaryTarget")

    def execute(self, context):

        blender_object = context.active_object
        TargetService.symmetrize_shape_key(blender_object, "PrimaryTarget", False)

        self.report({'INFO'}, "Target symmetrized")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_SymmetrizeLeftOperator)
