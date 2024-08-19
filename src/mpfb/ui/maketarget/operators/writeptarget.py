"""Operator for writing a MHMAT file."""

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from ....services import LogService
from ....services import ObjectService
from ....services import TargetService
from ...maketarget import MakeTargetObjectProperties
from mpfb import ClassManager

_LOG = LogService.get_logger("maketarget.writetarget")

class MPFB_OT_WritePtargetOperator(bpy.types.Operator, ExportHelper):
    """Write proxy-specific target to ptarget file"""
    bl_idname = "mpfb.write_maketarget_ptarget"
    bl_label = "Save proxy-specific target"
    bl_options = {'REGISTER'}

    filename_ext = '.ptarget'

    filter_glob: StringProperty(default='*.ptarget', options={'HIDDEN'})
    filepath: StringProperty(name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        blender_object = context.active_object
        if blender_object is None:
            return False

        object_type = ObjectService.get_object_type(blender_object)

        if not object_type or object_type == "Skeleton" or object_type == "Basemesh":
            return False

        if not context.active_object.data.shape_keys:
            return False

        return TargetService.has_target(blender_object, "PrimaryTarget")

    def invoke(self, context, event):
        blender_object = context.active_object
        name = MakeTargetObjectProperties.get_value("name", entity_reference=blender_object)
        self.filepath = bpy.path.clean_name(name, replace="-") + ".ptarget"
        return super().invoke(context, event)

    def execute(self, context):
        blender_object = context.active_object
        info = TargetService.get_shape_key_as_dict(blender_object, "PrimaryTarget")

        _LOG.dump("Shape key", info)

        with open(self.filepath, "w") as target_file:
            target_file.write(TargetService.shape_key_info_as_target_string(info))

        self.report({'INFO'}, "PTarget was saved as " + str(self.filepath))
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_WritePtargetOperator)
