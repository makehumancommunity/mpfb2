"""Operator for importing MHCLO clothes from asset library."""

import bpy
from bpy.props import StringProperty
from ....services import LogService
from ....services import ObjectService
from ....services import HumanService
from .... import ClassManager
from ...mpfboperator import MpfbOperator

_LOG = LogService.get_logger("assetlibrary.loadlibraryclothes")

class MPFB_OT_Load_Library_Clothes_Operator(MpfbOperator):
    """Load MHCLO from asset library"""
    bl_idname = "mpfb.load_library_clothes"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(name="filepath", description="Full path to asset", default="")
    object_type: StringProperty(name="object_type", description="type of the object", default="Clothes")
    material_type: StringProperty(name="material_type", description="type of material", default="MAKESKIN")

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):

        _LOG.debug("filepath", self.filepath)
        _LOG.debug("object_type", self.object_type)
        _LOG.debug("material_type", self.material_type)

        from ...assetlibrary.assetsettingspanel import ASSET_SETTINGS_PROPERTIES  # pylint: disable=C0415
        from ...mpfbcontext import MpfbContext

        ctx = MpfbContext(context=context, scene_properties=ASSET_SETTINGS_PROPERTIES)

        subdiv_levels = ctx.subdiv_levels

        blender_object = context.active_object

        rig = None
        basemesh = None

        if blender_object and not blender_object is None:
            if ObjectService.object_is_basemesh(blender_object):
                basemesh = blender_object
            else:
                basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(blender_object, "Basemesh")

            rig = ObjectService.find_object_of_type_amongst_nearest_relatives(blender_object, "Skeleton")

        if ctx.fit_to_body and basemesh is None:
            self.report({'ERROR'}, "Fit to body is enabled, but active object is not a base mesh")
            return {'FINISHED'}

        if ctx.delete_group and basemesh is None:
            self.report({'ERROR'}, "Set up delete group is enabled, but active object is not a base mesh")
            return {'FINISHED'}

        if ctx.interpolate_weights and basemesh is None:
            self.report({'ERROR'}, "interpolate weights is enabled, but active object is not a base mesh")
            return {'FINISHED'}

        if ctx.set_up_rigging and rig is None:
            self.report({'ERROR'}, "set up rigging is enabled, but could not find a rig to attach to")
            return {'FINISHED'}

        if not ctx.add_subdiv_modifier:
            subdiv_levels = 0

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        _LOG.debug("Will call add_mhclo_asset: (asset_type, material_type)", (self.object_type, self.material_type))
        HumanService.add_mhclo_asset(
            self.filepath, basemesh, asset_type=self.object_type, subdiv_levels=subdiv_levels,
            material_type=self.material_type, set_up_rigging=ctx.set_up_rigging,
            interpolate_weights=ctx.interpolate_weights, import_subrig=ctx.import_subrig, import_weights=ctx.import_weights)

        self.report({'INFO'}, "Clothes were loaded")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Library_Clothes_Operator)
