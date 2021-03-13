"""Operator for writing a MHMAT file."""

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.targetservice import TargetService
from mpfb.ui.maketarget import MakeTargetObjectProperties
from mpfb import ClassManager

_LOG = LogService.get_logger("maketarget.writetarget")
_LOG.set_level(LogService.DUMP)

class MPFB_OT_WriteTargetOperator(bpy.types.Operator, ExportHelper):
    """Write target to target file"""
    bl_idname = "mpfb.write_maketarget_target"
    bl_label = "Save target"
    bl_options = {'REGISTER'}

    filename_ext = '.target'

    filter_glob: StringProperty(default='*.target', options={'HIDDEN'})
    filepath: StringProperty(name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        if not ObjectService.object_is_basemesh(context.active_object):
            return False
        if context.active_object.data.shape_keys:
            return True
        return False

    def invoke(self, context, event):
        blender_object = context.active_object
        name = MakeTargetObjectProperties.get_value("name", entity_reference=blender_object)
        self.filepath = bpy.path.clean_name(name, replace="-") + ".target"
        return super().invoke(context, event)

    def execute(self, context):
        blender_object = context.active_object
        info = TargetService.get_shape_key_as_dict(blender_object, "PrimaryTarget")

        _LOG.dump("Shape key", info)

        with open(self.filepath, "w") as target_file:
            target_file.write(TargetService.shape_key_info_as_target_string(info))

        self.report({'INFO'}, "Target was saved as " + str(self.filepath))
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_WriteTargetOperator)
