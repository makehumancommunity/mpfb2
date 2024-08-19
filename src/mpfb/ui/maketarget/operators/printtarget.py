"""Operator for creating a template MakeTarget target."""

import bpy
from ....services import LogService
from ....services import ObjectService
from ....services import TargetService
from .... import ClassManager

_LOG = LogService.get_logger("maketarget.printtarget")

class MPFB_OT_PrintTargetOperator(bpy.types.Operator):
    """Dump target data to console"""
    bl_idname = "mpfb.print_maketarget_target"
    bl_label = "Print target"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        blender_object = context.active_object
        if blender_object is None:
            _LOG.trace("Blender object is None")
            return False

        object_type = ObjectService.get_object_type(blender_object)

        if not object_type or object_type == "Skeleton":
            _LOG.trace("Wrong object type", object_type)
            return False

        if not context.active_object.data.shape_keys:
            _LOG.trace("No shape keys", object_type)

        return TargetService.has_target(blender_object, "PrimaryTarget")

    def execute(self, context):
        blender_object = context.active_object
        info = TargetService.get_shape_key_as_dict(blender_object, "PrimaryTarget")

        _LOG.dump("Shape key", info)

        print(TargetService.shape_key_info_as_target_string(info))

        self.report({'INFO'}, "Target printed to console")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_PrintTargetOperator)
