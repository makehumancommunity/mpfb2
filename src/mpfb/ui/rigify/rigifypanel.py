"""This is the UI for the convert to rigify functionality."""

from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet
import bpy, os

_LOG = LogService.get_logger("ui.rigifypanel")

_LOC = os.path.dirname(__file__)
RIGIFY_PROPERTIES_DIR = os.path.join(_LOC, "properties")
RIGIFY_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(RIGIFY_PROPERTIES_DIR, prefix="RF_")

class MPFB_PT_Rigify_Panel(bpy.types.Panel):
    """The rigfy functionality panel."""

    bl_label = "Convert to rigify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("RIGCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene
        RIGIFY_PROPERTIES.draw_properties(scene, layout, ["produce", "keep_meta"])
        layout.operator("mpfb.convert_to_rigify")

ClassManager.add_class(MPFB_PT_Rigify_Panel)
