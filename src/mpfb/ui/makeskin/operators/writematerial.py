"""Operator for writing a MHMAT file."""

import bpy, os
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb import ClassManager
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial

_LOG = LogService.get_logger("makeskin.writematerial")

class MPFB_OT_WriteMaterialOperator(bpy.types.Operator, ExportHelper):
    """Write material to MHMAT file"""
    bl_idname = "mpfb.write_makeskin_material"
    bl_label = "Write material"
    bl_options = {'REGISTER'}

    filename_ext = '.mhmat'

    filter_glob: StringProperty(default='*.mhmat', options={'HIDDEN'})
    filepath: StringProperty(name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            if not hasattr(context.active_object, "MhObjectType"):
                return False
            return True
        return False

    def invoke(self, context, event):
        if not self.filepath:
            blend_filepath = context.active_object.MhMsName
            # just in case ... ;)
            if not blend_filepath:
                blend_filepath = "untitled"
            self.filepath = blend_filepath + self.filename_ext

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):

        obj = context.active_object

#===============================================================================
#         fnAbsolute = bpy.path.abspath(self.filepath)
#
#         if not hasMaterial(obj):
#             self.report({'ERROR'}, "Object does not have a material")
#             return {'FINISHED'}
#
#         mhmat = MHMat(obj)
#
#         checkImg = mhmat.checkAllTexturesAreSaved()
#         if checkImg:
#             self.report({'ERROR'}, checkImg)
#             return {'FINISHED'}
#
#         errtext = mhmat.writeMHmat(obj, fnAbsolute)
#         if errtext:
#             self.report({'ERROR'}, errtext)
#         else:
#             self.report({'INFO'}, "A material file was written")
#
#         # debug
#         print(mhmat)
#===============================================================================


        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_WriteMaterialOperator)
