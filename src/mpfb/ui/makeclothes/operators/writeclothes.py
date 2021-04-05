"""Operator for writing a MHCLO file."""

import bpy, os
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb import ClassManager

_LOG = LogService.get_logger("makeclothes.writematerial")

class MPFB_OT_WriteClothesOperator(bpy.types.Operator, ExportHelper):
    """Export clothes to MHCLO/OBJ"""
    bl_idname = "mpfb.write_makeclothes_clothes"
    bl_label = "Write clothes"
    bl_options = {'REGISTER'}

    filename_ext = '.mhclo'

    filter_glob: StringProperty(default='*.mhclo', options={'HIDDEN'})
    filepath: StringProperty(name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        # TODO: support blender materials
        #=======================================================================
        # if not self.filepath:
        #     blend_filepath = context.active_object.MhMsName
        #     # just in case ... ;)
        #     if not blend_filepath:
        #         blend_filepath = "untitled"
        #     self.filepath = blend_filepath + self.filename_ext
        #=======================================================================

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):

        blender_object = context.active_object

        file_name = bpy.path.abspath(self.filepath)

        self.report({'INFO'}, "The MHCLO file was written as " + file_name)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_WriteClothesOperator)
