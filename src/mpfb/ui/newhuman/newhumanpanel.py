"""File containing main UI for creating new humans"""

import bpy, os
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet

_LOG = LogService.get_logger("newhuman.newhumanpanel")

_LOC = os.path.dirname(__file__)
NEW_HUMAN_PROPERTIES_DIR = os.path.join(_LOC, "properties")
NEW_HUMAN_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(NEW_HUMAN_PROPERTIES_DIR, prefix="NH_")

class MPFB_PT_NewHuman_Panel(bpy.types.Panel):
    """New human main panel."""

    bl_label = "New human"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("MODELCATEGORY")
    #bl_options = {'DEFAULT_CLOSED'}

    def _create_box(self, layout, box_text, box_icon=None):
        _LOG.enter()
        box = layout.box()
        box.label(text=box_text, icon=box_icon)
        return box

    def _new_human(self, scene, layout):
        box = self._create_box(layout, "Create empty human", "TOOL_SETTINGS")
        NEW_HUMAN_PROPERTIES.draw_properties(scene, box, ["scale_factor"])
        box.operator('mpfb.create_human')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        self._new_human(scene, layout)


ClassManager.add_class(MPFB_PT_NewHuman_Panel)


