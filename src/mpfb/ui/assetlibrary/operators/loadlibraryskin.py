"""Operator for importing MHCLO skin from asset library."""

import bpy
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.humanservice import HumanService
from mpfb import ClassManager

_LOG = LogService.get_logger("assetlibrary.loadlibraryskin")

class MPFB_OT_Load_Library_Skin_Operator(bpy.types.Operator):
    """Load skin MHMAT from asset library"""
    bl_idname = "mpfb.load_library_skin"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(name="filepath", description="Full path to asset", default="")

    def execute(self, context):

        _LOG.debug("filepath", self.filepath)

        from mpfb.ui.assetlibrary.assetsettingspanel import ASSET_SETTINGS_PROPERTIES # pylint: disable=C0415

        scene = context.scene

        skin_type = ASSET_SETTINGS_PROPERTIES.get_value("skin_type", entity_reference=scene)
        material_instances = ASSET_SETTINGS_PROPERTIES.get_value("material_instances", entity_reference=scene)

        blender_object = context.active_object
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(blender_object, "Basemesh")
        bodyproxy = ObjectService.find_object_of_type_amongst_nearest_relatives(blender_object, "Proxymeshes")

        HumanService.set_character_skin(self.filepath, basemesh, bodyproxy=bodyproxy, skin_type=skin_type, material_instances=material_instances)

        self.report({'INFO'}, "Skin was loaded")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Library_Skin_Operator)
