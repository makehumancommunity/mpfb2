"""Operator for writing a target to the model library."""

import bpy, os
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from ....services import LogService
from ....services import ObjectService
from ....services import TargetService
from ....services import LocationService
from ...maketarget import MakeTargetObjectProperties
from .... import ClassManager

_LOG = LogService.get_logger("maketarget.writelibtarget")


class MPFB_OT_WriteLibTargetOperator(bpy.types.Operator):
    """Write target to model library. In order to do this, you must first have created a primary target on the mesh"""
    bl_idname = "mpfb.write_library_target"
    bl_label = "Save target"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        blender_object = context.active_object
        if blender_object is None:
            return False

        object_type = ObjectService.get_object_type(blender_object)

        if not object_type or object_type != "Basemesh":
            return False

        if not context.active_object.data.shape_keys:
            return False

        expected_name = MakeTargetObjectProperties.get_value("name", entity_reference=blender_object)
        _LOG.debug("Expected name", expected_name)
        if not expected_name:
            return False

        return TargetService.has_target(blender_object, expected_name)

    def execute(self, context):
        blender_object = context.active_object

        if blender_object.mode != "OBJECT":
            self.report({'ERROR'}, "Must be in object mode to save target file")
            return {'FINISHED'}

        expected_name = MakeTargetObjectProperties.get_value("name", entity_reference=blender_object)
        if not expected_name:
            self.report({'ERROR'}, "Must specify the name of the target")
            return {'FINISHED'}

        if not TargetService.has_target(blender_object, expected_name):
            self.report({'ERROR'}, "Must first create a MakeTarget primary target")
            return {'FINISHED'}

        info = TargetService.get_shape_key_as_dict(blender_object, expected_name)

        _LOG.dump("Shape key", info)

        data_dir = LocationService.get_user_data("custom")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        file_path = os.path.join(data_dir, expected_name + ".target")
        with open(file_path, "w") as target_file:
            target_file.write(TargetService.shape_key_info_as_target_string(info))

        self.report({'INFO'}, "Target was saved as custom target, but you need to restart Blender for it to be visible")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_WriteLibTargetOperator)
