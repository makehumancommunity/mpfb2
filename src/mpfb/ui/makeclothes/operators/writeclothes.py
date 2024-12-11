"""Operator for saving a MHCLO file."""

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from ....services import LogService
from ...makeclothes.operators.clothescommon import ClothesCommon
from .... import ClassManager

_LOG = LogService.get_logger("makeclothes.writeclothes")

class MPFB_OT_WriteClothesOperator(ClothesCommon, ExportHelper):
    """Export the asset to MHCLO + MHMAT + obj, with filenames based on the mhclo file. Use this if you don't want to store the asset in your local asset library"""
    bl_idname = "mpfb.write_makeclothes_clothes"
    bl_label = "Save as files"
    bl_options = {'REGISTER'}

    filename_ext = '.mhclo'

    filter_glob: StringProperty(default='*.mhclo')
    filepath: StringProperty(name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):

        if not self.filepath:
            self.report({'ERROR'}, "No file path specified")
            return {'CANCELLED'}

        file_name = bpy.path.abspath(self.filepath)

        return self.generic_execute(context, file_name)


ClassManager.add_class(MPFB_OT_WriteClothesOperator)
