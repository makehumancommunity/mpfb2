"""Operator for importing MHCLO clothes."""

import bpy, os
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from ....services import LogService
from ....services import ObjectService
from ....services import MaterialService
from ....services import ClothesService
from ....services import HumanService
from mpfb.entities.clothes.mhclo import Mhclo
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from .... import ClassManager

_LOG = LogService.get_logger("loadclothes.loadclothes")

class MPFB_OT_Load_Clothes_Operator(bpy.types.Operator, ImportHelper):
    """Load clothes from MHCLO file"""
    bl_idname = "mpfb.load_clothes"
    bl_label = "Load clothes from file"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(default='*.mhclo', options={'HIDDEN'})

    def execute(self, context):

        from ...loadclothes.loadclothespanel import LOAD_CLOTHES_PROPERTIES # pylint: disable=C0415
        from ...assetlibrary.assetsettingspanel import ASSET_SETTINGS_PROPERTIES # pylint: disable=C0415

        scene = context.scene

        object_type = LOAD_CLOTHES_PROPERTIES.get_value("object_type", entity_reference=scene)
        material_type = ASSET_SETTINGS_PROPERTIES.get_value("material_type", entity_reference=scene)
        fit_to_body = ASSET_SETTINGS_PROPERTIES.get_value("fit_to_body", entity_reference=scene)
        delete_group = ASSET_SETTINGS_PROPERTIES.get_value("delete_group", entity_reference=scene)
        specific_delete_group = ASSET_SETTINGS_PROPERTIES.get_value("specific_delete_group", entity_reference=scene)
        set_up_rigging = ASSET_SETTINGS_PROPERTIES.get_value("set_up_rigging", entity_reference=scene)
        interpolate_weights = ASSET_SETTINGS_PROPERTIES.get_value("interpolate_weights", entity_reference=scene)
        import_subrig = ASSET_SETTINGS_PROPERTIES.get_value("import_subrig", entity_reference=scene)
        import_weights = ASSET_SETTINGS_PROPERTIES.get_value("import_weights", entity_reference=scene)
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

        if basemesh and fit_to_body:
            subdiv = 0
            if add_subdiv_modifier:
                subdiv = subdiv_levels
            clothes = HumanService.add_mhclo_asset(self.filepath, basemesh, asset_type=object_type, subdiv_levels=subdiv, material_type="MAKESKIN", set_up_rigging=(rig is not None), interpolate_weights=True, import_subrig=import_subrig, import_weights=import_weights)
        else:
            mhclo = Mhclo()
            mhclo.load(self.filepath) # pylint: disable=E1101
            clothes = mhclo.load_mesh(context)
            GeneralObjectProperties.set_value("object_type", object_type, entity_reference=clothes)
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
                ClothesService.set_up_rigging(
                    basemesh, clothes, rig, mhclo, interpolate_weights=interpolate_weights,
                    import_subrig=import_subrig, import_weights=import_weights)
            else:
                if basemesh:
                    clothes.parent = basemesh

        if not clothes or clothes is None:
            self.report({'ERROR'}, "failed to import the clothes mesh")
            return {'FINISHED'}

        if makeclothes_metadata:
            ClothesService.set_makeclothes_object_properties_from_mhclo(clothes, mhclo, delete_group_name=delete_name)

        self.report({'INFO'}, "Clothes were loaded")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Clothes_Operator)
