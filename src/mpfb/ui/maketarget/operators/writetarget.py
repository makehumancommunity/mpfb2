"""Operator for writing a MHMAT file."""

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.targetservice import TargetService
from mpfb.ui.maketarget import MakeTargetObjectProperties
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb import ClassManager

_LOG = LogService.get_logger("maketarget.writetarget")

class MPFB_OT_WriteTargetOperator(bpy.types.Operator, ExportHelper):
    """Write target to target file. In order to do this, you must first have created a primary target on the mesh."""
    bl_idname = "mpfb.write_maketarget_target"
    bl_label = "Save target"
    bl_options = {'REGISTER'}

    filename_ext = '.target'

    filter_glob: StringProperty(default='*.target', options={'HIDDEN'})
    filepath: StringProperty(name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        blender_object = context.active_object
        if blender_object is None:
            return False

        object_type = GeneralObjectProperties.get_value("object_type", entity_reference=blender_object)

        if not object_type or object_type != "Basemesh":
            return False

        if not context.active_object.data.shape_keys:
            return False

        return TargetService.has_target(blender_object, "PrimaryTarget")

    def invoke(self, context, event):
        blender_object = context.active_object
        name = MakeTargetObjectProperties.get_value("name", entity_reference=blender_object)
        self.filepath = bpy.path.clean_name(name, replace="-") + ".target"
        return super().invoke(context, event)

    def execute(self, context):
        blender_object = context.active_object

        if not TargetService.has_target(blender_object, "PrimaryTarget"):
            self.report({'ERROR'}, "Must first create a MakeTarget primary target")
            return {'FINISHED'}

        info = TargetService.get_shape_key_as_dict(blender_object, "PrimaryTarget")

        _LOG.dump("Shape key", info)

        with open(self.filepath, "w") as target_file:
            target_file.write(TargetService.shape_key_info_as_target_string(info))

        self.report({'INFO'}, "Target was saved as " + str(self.filepath))
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_WriteTargetOperator)
