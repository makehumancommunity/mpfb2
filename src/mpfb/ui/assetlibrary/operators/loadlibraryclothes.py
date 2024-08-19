"""Operator for importing MHCLO clothes from asset library."""

import bpy
from bpy.props import StringProperty
from ....services import LogService
from ....services import ObjectService
from ....services import HumanService
from mpfb import ClassManager

_LOG = LogService.get_logger("assetlibrary.loadlibraryclothes")

class MPFB_OT_Load_Library_Clothes_Operator(bpy.types.Operator):
    """Load MHCLO from asset library"""
    bl_idname = "mpfb.load_library_clothes"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(name="filepath", description="Full path to asset", default="")
    object_type: StringProperty(name="object_type", description="type of the object", default="Clothes")
    material_type: StringProperty(name="material_type", description="type of material", default="MAKESKIN")

    def execute(self, context):

        _LOG.debug("filepath", self.filepath)
        _LOG.debug("object_type", self.object_type)
        _LOG.debug("material_type", self.material_type)

        from mpfb.ui.assetlibrary.assetsettingspanel import ASSET_SETTINGS_PROPERTIES # pylint: disable=C0415

        scene = context.scene

        fit_to_body = ASSET_SETTINGS_PROPERTIES.get_value("fit_to_body", entity_reference=scene)
        delete_group = ASSET_SETTINGS_PROPERTIES.get_value("delete_group", entity_reference=scene)
        # TODO: specific_delete_group = ASSET_SETTINGS_PROPERTIES.get_value("specific_delete_group", entity_reference=scene)
        set_up_rigging = ASSET_SETTINGS_PROPERTIES.get_value("set_up_rigging", entity_reference=scene)
        interpolate_weights = ASSET_SETTINGS_PROPERTIES.get_value("interpolate_weights", entity_reference=scene)
        import_subrig = ASSET_SETTINGS_PROPERTIES.get_value("import_subrig", entity_reference=scene)
        import_weights = ASSET_SETTINGS_PROPERTIES.get_value("import_weights", entity_reference=scene)
        # TODO: makeclothes_metadata = ASSET_SETTINGS_PROPERTIES.get_value("makeclothes_metadata", entity_reference=scene)
        add_subdiv_modifier = ASSET_SETTINGS_PROPERTIES.get_value("add_subdiv_modifier", entity_reference=scene)
        subdiv_levels = ASSET_SETTINGS_PROPERTIES.get_value("subdiv_levels", entity_reference=scene)

        blender_object = context.active_object

        rig = None
        basemesh = None

        if blender_object and not blender_object is None:
            if ObjectService.object_is_basemesh(blender_object):
                basemesh = blender_object
            else:
                basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(blender_object, "Basemesh")

            rig = ObjectService.find_object_of_type_amongst_nearest_relatives(blender_object, "Skeleton")

        if fit_to_body and basemesh is None:
            self.report({'ERROR'}, "Fit to body is enabled, but active object is not a base mesh")
            return {'FINISHED'}

        if delete_group and basemesh is None:
            self.report({'ERROR'}, "Set up delete group is enabled, but active object is not a base mesh")
            return {'FINISHED'}

        if interpolate_weights and basemesh is None:
            self.report({'ERROR'}, "interpolate weights is enabled, but active object is not a base mesh")
            return {'FINISHED'}

        if set_up_rigging and rig is None:
            self.report({'ERROR'}, "set up rigging is enabled, but could not find a rig to attach to")
            return {'FINISHED'}

        if not add_subdiv_modifier:
            subdiv_levels = 0

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        _LOG.debug("Will call add_mhclo_asset: (asset_type, material_type)", (self.object_type, self.material_type))
        HumanService.add_mhclo_asset(
            self.filepath, basemesh, asset_type=self.object_type, subdiv_levels=subdiv_levels,
            material_type=self.material_type, set_up_rigging=set_up_rigging,
            interpolate_weights=interpolate_weights, import_subrig=import_subrig, import_weights=import_weights)

        self.report({'INFO'}, "Clothes were loaded")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Library_Clothes_Operator)
