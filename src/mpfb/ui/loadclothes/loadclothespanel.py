"""This file contains the load clothes panel."""

from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet
import bpy, os

_LOG = LogService.get_logger("ui.loadclothespanel")

#_LOC = os.path.dirname(__file__)
#LOG_LEVELS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
#LOG_LEVELS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(LOG_LEVELS_PROPERTIES_DIR, prefix="LL_")
#LOG_LEVELS_PROPERTIES.add_property(_LEVELS_LIST_PROP, _populate_list)

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
        #LOG_LEVELS_PROPERTIES.draw_properties(scene, layout, ["available_loggers", "chosen_level"])
        layout.operator("mpfb.load_clothes")

ClassManager.add_class(MPFB_PT_Load_Clothes_Panel)

