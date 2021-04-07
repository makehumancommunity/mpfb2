"""This file contains the load clothes panel."""

from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet
import bpy, os

_LOG = LogService.get_logger("ui.loadclothespanel")

_LOC = os.path.dirname(__file__)
LOAD_CLOTHES_PROPERTIES_DIR = os.path.join(_LOC, "properties")
LOAD_CLOTHES_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(LOAD_CLOTHES_PROPERTIES_DIR, prefix="LC_")

class MPFB_PT_Load_Clothes_Panel(bpy.types.Panel):
    """UI for loading clothes."""
    bl_label = "Load clothes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("CLOTHESCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene
        LOAD_CLOTHES_PROPERTIES.draw_properties(scene, layout, [
            "object_type",
            "material_type",
            "fit_to_body",
            "delete_group",
            "set_up_rigging",
            "interpolate_weights",
            "makeclothes_metadata"
            ])
        layout.operator("mpfb.load_clothes")

ClassManager.add_class(MPFB_PT_Load_Clothes_Panel)

