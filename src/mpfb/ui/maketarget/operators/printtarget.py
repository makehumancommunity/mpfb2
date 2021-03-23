"""Operator for creating a template MakeTarget target."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.targetservice import TargetService
from mpfb import ClassManager

_LOG = LogService.get_logger("maketarget.printtarget")

class MPFB_OT_PrintTargetOperator(bpy.types.Operator):
    """Dump target data to console"""
    bl_idname = "mpfb.print_maketarget_target"
    bl_label = "Print target"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if not ObjectService.object_is_basemesh(context.active_object):
            return False
        if context.active_object.data.shape_keys:
            return True
        return False

    def execute(self, context):
        blender_object = context.active_object
        info = TargetService.get_shape_key_as_dict(blender_object, "PrimaryTarget")

        _LOG.dump("Shape key", info)

        print(TargetService.shape_key_info_as_target_string(info))

        self.report({'INFO'}, "Target printed to console")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_PrintTargetOperator)
