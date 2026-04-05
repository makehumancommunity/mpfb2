"""Operator for writing a MHMAT file."""

import bpy, os
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from .....services import LogService
from .....services import LocationService
from .....services import MaterialService
from .....services import ObjectService
from ..... import ClassManager
from .....entities.material.makeskinmaterial import MakeSkinMaterial
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("makeskin.writelibrary")

@pollstrategy(PollStrategy.BASEMESH_OR_BODY_PROXY_ACTIVE)
class MPFB_OT_WriteLibraryOperator(MpfbOperator):
    """Save material in the user skins directory to make it available as new body skin"""
    bl_idname = "mpfb.write_makeskin_to_library"
    bl_label = "Store as skin"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        from ...makeskin import MakeSkinObjectProperties  # pylint: disable=C0415
        from ....mpfbcontext import MpfbContext  # pylint: disable=C0415

        ctx = MpfbContext(context=context, object_properties=MakeSkinObjectProperties)

        if not ctx.name:
            self.report({'ERROR'}, "The material must have a name")
            return {'FINISHED'}

        skindir = LocationService.get_user_data("skins")
        if not os.path.exists(skindir):
            os.makedirs(skindir)

        normalized_name = ctx.name.replace(" ", "_").lower()

        file_name = os.path.abspath(os.path.join(skindir, normalized_name))
        if not os.path.exists(file_name):
            os.makedirs(file_name)

        file_name = os.path.join(file_name, normalized_name + ".mhmat")

        _LOG.debug("file_name", file_name)

        if not MaterialService.has_materials(ctx.active_object):
            self.report({'ERROR'}, "Object does not have a material")
            return {'FINISHED'}

        material = MakeSkinMaterial()
        material.populate_from_object(ctx.active_object)

        image_file_error = material.check_that_all_textures_are_saved(ctx.active_object)
        if not image_file_error is None:
            self.report({'ERROR'}, image_file_error)
            return {'FINISHED'}

        material.export_to_disk(file_name)

        self.report({'INFO'}, "The MHMAT file was written as " + file_name)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_WriteLibraryOperator)
