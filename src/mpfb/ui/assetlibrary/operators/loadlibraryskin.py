"""Operator for importing MHCLO skin from asset library."""

import bpy, os
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.materialservice import MaterialService
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from mpfb.entities.material.enhancedskinmaterial import EnhancedSkinMaterial
from mpfb import ClassManager

_LOG = LogService.get_logger("assetlibrary.loadlibraryskin")

class MPFB_OT_Load_Library_Skin_Operator(bpy.types.Operator):
    """Load skin MHMAT from asset library."""
    bl_idname = "mpfb.load_library_skin"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = StringProperty(name="filepath", description="Full path to asset", default="")

    def execute(self, context):

        _LOG.debug("filepath", self.filepath)

        from mpfb.ui.assetlibrary.assetsettingspanel import ASSET_SETTINGS_PROPERTIES # pylint: disable=C0415

        scene = context.scene

        skin_type = ASSET_SETTINGS_PROPERTIES.get_value("skin_type", entity_reference=scene)
        material_instances = ASSET_SETTINGS_PROPERTIES.get_value("material_instances", entity_reference=scene)

        blender_object = context.active_object

        MaterialService.delete_all_materials(blender_object)

        name = blender_object.name + ".body"

        if skin_type == "MAKESKIN":
            makeskin_material = MakeSkinMaterial()
            makeskin_material.populate_from_mhmat(self.filepath)
            blender_material = MaterialService.create_empty_material(name, blender_object)
            makeskin_material.apply_node_tree(blender_material)

        if skin_type in ["ENHANCED", "ENHANCED_SSS"]:
            presets = dict()
            presets["skin_material_type"] = skin_type
            presets["scale_factor"] = "METER" # TODO: get from active object

            enhanced_material = EnhancedSkinMaterial(presets)
            enhanced_material.populate_from_mhmat(self.filepath)
            blender_material = MaterialService.create_empty_material(name, blender_object)
            enhanced_material.apply_node_tree(blender_material)

        self.report({'INFO'}, "Skin was loaded")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Library_Skin_Operator)
