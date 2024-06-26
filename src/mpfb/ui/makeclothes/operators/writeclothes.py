"""Operator for saving a MHCLO file."""

import bpy, os
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.services.clothesservice import ClothesService
from mpfb.services.materialservice import MaterialService
from mpfb.ui.makeclothes import MakeClothesObjectProperties
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from mpfb.ui.makeclothes.operators.clothescommon import ClothesCommon
from mpfb import ClassManager

_LOG = LogService.get_logger("makeclothes.writeclothes")

class MPFB_OT_WriteClothesOperator(bpy.types.Operator, ExportHelper, ClothesCommon):
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
