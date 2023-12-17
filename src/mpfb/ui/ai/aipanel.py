"""This file contains the AI panel."""

from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.ui.abstractpanel import Abstract_Panel
import bpy, os

_LOG = LogService.get_logger("ui.aipanel")

_LOC = os.path.dirname(__file__)
AI_PROPERTIES_DIR = os.path.join(_LOC, "properties")
AI_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(AI_PROPERTIES_DIR, prefix="AIP_")

class MPFB_PT_Ai_Panel(Abstract_Panel):
    """UI for various AI-related functions."""
    bl_label = "AI"
    bl_category = UiService.get_value("OPERATIONSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Operations_Panel"

    def _openpose(self, scene, layout):
        box = self._create_box(layout, "OpenPose")
        AI_PROPERTIES.draw_properties(scene, box, ["zoom"])
        box.operator("mpfb.save_openpose")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene
        self._openpose(scene, layout)

ClassManager.add_class(MPFB_PT_Ai_Panel)

