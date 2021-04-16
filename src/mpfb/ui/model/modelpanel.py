"""File containing main UI for modeling humans"""

import bpy, os
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet

_LOG = LogService.get_logger("model.modelpanel")

_LOC = os.path.dirname(__file__)
MODEL_PROPERTIES_DIR = os.path.join(_LOC, "properties")
MODEL_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(MODEL_PROPERTIES_DIR, prefix="MOD_")

class MPFB_PT_Model_Panel(bpy.types.Panel):
    """Human modeling panel."""

    bl_label = "Model"
    bl_idname = "MPFB_PT_Model_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    def _create_box(self, layout, box_text):
        _LOG.enter()
        box = layout.box()
        box.label(text=box_text)
        return box

    def _refit(self, scene, layout):
        box = self._create_box(layout, "Refit")
        #=======================================================================
        # NEW_HUMAN_PROPERTIES.draw_properties(scene, box, [
        #     "scale_factor",
        #     "detailed_helpers",
        #     "extra_vertex_groups",
        #     "mask_helpers"
        #     ])
        # box.operator('mpfb.create_human')
        #=======================================================================


    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        self._refit(scene, layout)

ClassManager.add_class(MPFB_PT_Model_Panel)

from ._modelsubpanels import *
