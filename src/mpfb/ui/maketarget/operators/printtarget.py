"""Operator for creating a template MakeTarget target."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.targetservice import TargetService
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb import ClassManager

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
            return False

        object_type = GeneralObjectProperties.get_value("object_type", entity_reference=blender_object)

        if not object_type or object_type == "Skeleton":
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
