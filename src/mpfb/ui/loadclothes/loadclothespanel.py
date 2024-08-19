"""This file contains the load clothes panel."""

from mpfb._classmanager import ClassManager
from ...services import LogService
from ...services import UiService
from ...services import SceneConfigSet
from ..abstractpanel import Abstract_Panel
import bpy, os

_LOG = LogService.get_logger("ui.loadclothespanel")

_LOC = os.path.dirname(__file__)
LOAD_CLOTHES_PROPERTIES_DIR = os.path.join(_LOC, "properties")
LOAD_CLOTHES_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(LOAD_CLOTHES_PROPERTIES_DIR, prefix="LC_")

class MPFB_PT_Load_Clothes_Panel(Abstract_Panel):
    """UI for loading MHCLO files."""
    bl_label = "Load MHCLO"
    bl_category = UiService.get_value("CLOTHESCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Assets_Panel"

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene
        LOAD_CLOTHES_PROPERTIES.draw_properties(scene, layout, [
            "object_type"
            ])
        layout.operator("mpfb.load_clothes")

ClassManager.add_class(MPFB_PT_Load_Clothes_Panel)

