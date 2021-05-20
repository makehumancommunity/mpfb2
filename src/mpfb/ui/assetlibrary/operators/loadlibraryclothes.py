"""Operator for importing MHCLO clothes from asset library."""

import bpy, os
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.materialservice import MaterialService
from mpfb.services.clothesservice import ClothesService
from mpfb.entities.mhclo import Mhclo
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from mpfb import ClassManager

_LOG = LogService.get_logger("assetlibrary.loadlibraryclothes")
_LOG.set_level(LogService.DUMP)

class MPFB_OT_Load_Library_Clothes_Operator(bpy.types.Operator):
    """Load MHCLO from asset library."""
    bl_idname = "mpfb.load_library_clothes"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = StringProperty(name="filepath", description="Full path to asset", default="")
    object_type = StringProperty(name="object_type", description="type of the object", default="Clothes")

    def execute(self, context):

        _LOG.debug("filepath", self.filepath)
        _LOG.debug("object_type", self.object_type)

        from mpfb.ui.assetlibrary.assetsettingspanel import ASSET_SETTINGS_PROPERTIES # pylint: disable=C0415

        scene = context.scene

        object_type = self.object_type
        material_type = "MAKESKIN" # TODO: some kind of operator argument
        fit_to_body = ASSET_SETTINGS_PROPERTIES.get_value("fit_to_body", entity_reference=scene)
        delete_group = ASSET_SETTINGS_PROPERTIES.get_value("delete_group", entity_reference=scene)
        specific_delete_group = ASSET_SETTINGS_PROPERTIES.get_value("specific_delete_group", entity_reference=scene)
        set_up_rigging = ASSET_SETTINGS_PROPERTIES.get_value("set_up_rigging", entity_reference=scene)
        interpolate_weights = ASSET_SETTINGS_PROPERTIES.get_value("interpolate_weights", entity_reference=scene)
        makeclothes_metadata = ASSET_SETTINGS_PROPERTIES.get_value("makeclothes_metadata", entity_reference=scene)
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

        mhclo = Mhclo()
        mhclo.load(self.filepath) # pylint: disable=E1101
        clothes = mhclo.load_mesh(context)

        if not clothes or clothes is None:
            self.report({'ERROR'}, "failed to import the clothes mesh")
            return {'FINISHED'}

        asset_dir = os.path.basename(os.path.dirname(os.path.realpath(self.filepath)))
        asset_source = asset_dir + "/" + os.path.basename(self.filepath)

        GeneralObjectProperties.set_value("object_type", object_type, entity_reference=clothes)
        GeneralObjectProperties.set_value("asset_source", asset_source, entity_reference=clothes)

        bpy.ops.object.shade_smooth()

        if not material_type == "PRINCIPLED":
            MaterialService.delete_all_materials(clothes)

        if material_type == "MAKESKIN" and not mhclo.material is None:
            makeskin_material = MakeSkinMaterial()
            makeskin_material.populate_from_mhmat(mhclo.material)
            name = os.path.basename(mhclo.material)
            blender_material = MaterialService.create_empty_material(name, clothes)
            makeskin_material.apply_node_tree(blender_material)

        if fit_to_body:
            ClothesService.fit_clothes_to_human(clothes, basemesh, mhclo)
            mhclo.set_scalings(context, basemesh)

        delete_name = "Delete"
        if delete_group:
            if specific_delete_group:
                delete_name = str(os.path.basename(self.filepath)) # pylint: disable=E1101
                delete_name = delete_name.replace(".mhclo", "")
                delete_name = delete_name.replace(".MHCLO", "")
                delete_name = delete_name.replace(" ", "_")
                delete_name = "Delete." + delete_name
            ClothesService.update_delete_group(mhclo, basemesh, replace_delete_group=False, delete_group_name=delete_name)

        if set_up_rigging:
            clothes.location = (0.0, 0.0, 0.0)
            clothes.parent = rig
            modifier = clothes.modifiers.new("Armature", 'ARMATURE')
            modifier.object = rig
            if interpolate_weights:
                ClothesService.interpolate_weights(basemesh, clothes, rig, mhclo)

        if makeclothes_metadata:
            ClothesService.set_makeclothes_object_properties_from_mhclo(clothes, mhclo, delete_group_name=delete_name)

        if add_subdiv_modifier:
            modifier = clothes.modifiers.new("Subdivision", 'SUBSURF')
            modifier.levels = 0
            modifier.render_levels = subdiv_levels

        self.report({'INFO'}, "Clothes were loaded")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Library_Clothes_Operator)
