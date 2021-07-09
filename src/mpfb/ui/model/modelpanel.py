"""File containing main UI for modeling humans"""

import bpy, os
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet

_LOG = LogService.get_logger("model.modelpanel")

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

    def _general(self, scene, layout):
        box = self._create_box(layout, "General")
        box.operator('mpfb.refit_human')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        self._general(scene, layout)

    @classmethod
    def poll(cls, context):
        return ObjectService.object_is_basemesh(context.active_object)

ClassManager.add_class(MPFB_PT_Model_Panel)

from ._macrosubpanel import MPFB_PT_Macro_Sub_Panel
from ._modelsubpanels import *
