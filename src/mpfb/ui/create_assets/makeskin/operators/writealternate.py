"""Operator for writing a MHMAT file."""

import bpy, os
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from .....services import LogService
from .....services import AssetService
from .....services import LocationService
from .....services import MaterialService
from .....services import ObjectService
from .....entities.objectproperties import GeneralObjectProperties
from ..... import ClassManager
from .....entities.material.makeskinmaterial import MakeSkinMaterial
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("makeskin.writealternate")

class MPFB_OT_WriteAlternateOperator(MpfbOperator):
    """Save material along the mesh asset to make it available as an alternate material. The name property will be used as filename. For skins, use store skin operator instead"""
    bl_idname = "mpfb.write_alternate"
    bl_label = "Store as alternate"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    @classmethod
    def poll(cls, context):
        if ObjectService.object_is_basemesh_or_body_proxy(context.active_object):
            return False
        return ObjectService.object_is_any_makehuman_mesh(context.active_object)

    def hardened_execute(self, context):
        from ...makeskin import MakeSkinObjectProperties  # pylint: disable=C0415
        from ....mpfbcontext import MpfbContext  # pylint: disable=C0415

        ctx = MpfbContext(context=context, object_properties=MakeSkinObjectProperties)

        if not MaterialService.has_materials(ctx.active_object):
            self.report({'ERROR'}, "Object does not have a material")
            return {'FINISHED'}

        if not ctx.name:
            self.report({'ERROR'}, "The material must have a name")
            return {'FINISHED'}

        name = str(ctx.name).replace(" ", "_").lower()

        otype = ObjectService.get_object_type(ctx.active_object)
        _LOG.debug("otype", otype)
        if not otype:
            self.report({'ERROR'}, "Object is not a makehuman mesh")
            return {'FINISHED'}
        source = GeneralObjectProperties.get_value("asset_source", entity_reference=ctx.active_object)
        _LOG.debug("source", source)
        if not source:
            self.report({'ERROR'}, "Object does not have an asset source")
            return {'FINISHED'}

        full_path = AssetService.find_asset_absolute_path(source, str(otype).lower())
        if not full_path:
            self.report({'ERROR'}, "Object does not have an asset path")
            return {'FINISHED'}

        dirn = os.path.dirname(full_path)
        adir = os.path.join(dirn, name)

        if not os.path.exists(adir):
            os.makedirs(adir)

        file_name = os.path.join(adir, name + ".mhmat")

        _LOG.debug("file_name", file_name)

        material = MakeSkinMaterial()
        material.populate_from_object(ctx.active_object)

        dirn = os.path.dirname(file_name)
        bn = os.path.basename(file_name).replace(".mhmat", "")

        image_file_error = material.check_that_all_textures_are_saved(ctx.active_object, dirn, bn)
        if image_file_error is not None:
            self.report({'ERROR'}, image_file_error)
            return {'FINISHED'}

        material.export_to_disk(file_name)

        self.report({'INFO'}, "The MHMAT file was written as " + file_name)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_WriteAlternateOperator)
