"""Operator for importing PROXY from asset library."""

import bpy, os
from bpy.props import StringProperty
from ....services import LogService
from ....services import ObjectService
from ....services import MaterialService
from ....services import ClothesService
from ....services import RigService
from mpfb.entities.clothes.mhclo import Mhclo
from mpfb.entities.socketobject import ALL_EXTRA_GROUPS
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from .... import ClassManager

_LOG = LogService.get_logger("assetlibrary.loadlibraryproxy")

class MPFB_OT_Load_Library_Proxy_Operator(bpy.types.Operator):
    """Load PROXY from asset library"""
    bl_idname = "mpfb.load_library_proxy"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(name="filepath", description="Full path to asset", default="")
    object_type: StringProperty(name="object_type", description="type of the object", default="Proxymeshes")

    def execute(self, context):

        _LOG.debug("filepath", self.filepath)

        from ...assetlibrary.assetsettingspanel import ASSET_SETTINGS_PROPERTIES # pylint: disable=C0415

        scene = context.scene

        object_type = self.object_type
        material_type = "MAKESKIN" # TODO: some kind of operator argument
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
        mask_base_mesh = ASSET_SETTINGS_PROPERTIES.get_value("mask_base_mesh", entity_reference=scene)

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
            self.report({'ERROR'}, "failed to import the proxy")
            return {'FINISHED'}

        asset_dir = os.path.basename(os.path.dirname(os.path.realpath(self.filepath)))
        asset_source = asset_dir + "/" + os.path.basename(self.filepath)

        scale_factor = GeneralObjectProperties.get_value("scale_factor", entity_reference=basemesh)

        GeneralObjectProperties.set_value("object_type", "Proxymeshes", entity_reference=clothes)
        GeneralObjectProperties.set_value("asset_source", asset_source, entity_reference=clothes)
        GeneralObjectProperties.set_value("scale_factor", scale_factor, entity_reference=clothes)

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

        if set_up_rigging:
            clothes.location = (0.0, 0.0, 0.0)

            ClothesService.set_up_rigging(
                basemesh, clothes, rig, mhclo, interpolate_weights=interpolate_weights,
                import_subrig=import_subrig, import_weights=import_weights)

        if add_subdiv_modifier:
            modifier = clothes.modifiers.new("Subdivision", 'SUBSURF')
            modifier.levels = 0
            modifier.render_levels = subdiv_levels

        if mask_base_mesh:
            modifier = basemesh.modifiers.new("Hide base mesh", 'MASK')
            modifier.vertex_group = "body"
            modifier.invert_vertex_group = True

        #if makeclothes_metadata:
        #    ClothesService.set_makeclothes_object_properties_from_mhclo(clothes, mhclo, delete_group_name=delete_name)

        _LOG.debug("clothes, uuid", (clothes, mhclo.uuid))
        if clothes and mhclo.uuid:
            GeneralObjectProperties.set_value("uuid", mhclo.uuid, entity_reference=clothes)
            _LOG.debug("Has extra vgroups", mhclo.uuid in ALL_EXTRA_GROUPS)
            if mhclo.uuid in ALL_EXTRA_GROUPS:
                for vgroup_name in ALL_EXTRA_GROUPS[mhclo.uuid].keys():
                    _LOG.debug("Will create vgroup", vgroup_name)
                    vgroup = clothes.vertex_groups.new(name=vgroup_name)
                    vgroup.add(ALL_EXTRA_GROUPS[mhclo.uuid][vgroup_name], 1.0, 'ADD')

        self.report({'INFO'}, "Proxy was loaded")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Library_Proxy_Operator)
