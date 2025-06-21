"""Operator for writing a MHMAT file."""

import bpy, os
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from ....services import LogService
from ....services import LocationService
from ....services import MaterialService
from ....services import ObjectService
from .... import ClassManager
from ....entities.material.makeskinmaterial import MakeSkinMaterial

_LOG = LogService.get_logger("makeskin.writelibrary")

class MPFB_OT_WriteLibraryOperator(bpy.types.Operator):
    """Save material in the user skins directory to make it available as new body skin"""
    bl_idname = "mpfb.write_makeskin_to_library"
    bl_label = "Store as skin"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return ObjectService.object_is_basemesh_or_body_proxy(context.active_object)

    def execute(self, context):

        blender_object = context.active_object

        from ...makeskin import MakeSkinObjectProperties
        name = MakeSkinObjectProperties.get_value("name", entity_reference=blender_object)

        if not name:
            self.report({'ERROR'}, "The material must have a name")
            return {'FINISHED'}

        skindir = LocationService.get_user_data("skins")
        if not os.path.exists(skindir):
            os.makedirs(skindir)

        normalized_name = name.replace(" ", "_").lower()

        file_name = os.path.abspath(os.path.join(skindir, normalized_name))
        if not os.path.exists(file_name):
            os.makedirs(file_name)

        file_name = os.path.join(file_name, normalized_name + ".mhmat")

        _LOG.debug("file_name", file_name)

        if not MaterialService.has_materials(blender_object):
            self.report({'ERROR'}, "Object does not have a material")
            return {'FINISHED'}

        material = MakeSkinMaterial()
        material.populate_from_object(blender_object)

        image_file_error = material.check_that_all_textures_are_saved(blender_object)
        if not image_file_error is None:
            self.report({'ERROR'}, image_file_error)
            return {'FINISHED'}

        material.export_to_disk(file_name)

        self.report({'INFO'}, "The MHMAT file was written as " + file_name)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_WriteLibraryOperator)
