"""Operator for writing a MHMAT file."""

import bpy, os
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb import ClassManager
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial

_LOG = LogService.get_logger("makeskin.writematerial")
_LOG.set_level(LogService.DUMP)

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
            return MaterialService.has_materials(context.active_object)
        return False

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

        if not MaterialService.has_materials(blender_object):
            self.report({'ERROR'}, "Object does not have a material")
            return {'FINISHED'}

        material = MakeSkinMaterial()
        material.populate_from_object(blender_object)

        mhmat_string = material.as_mhmat()
        _LOG.dump("material", mhmat_string)

        image_file_error = material.check_that_all_textures_are_saved(blender_object)
        if not image_file_error is None:
            self.report({'ERROR'}, image_file_error)
            return {'FINISHED'}

        # TODO: copy normalized images

        with open(file_name, "w") as mhmat:
            mhmat.write(mhmat_string)

        self.report({'INFO'}, "The MHMAT file was written as " + file_name)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_WriteMaterialOperator)
