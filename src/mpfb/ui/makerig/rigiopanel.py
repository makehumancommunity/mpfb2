"""File containing load/save rig and weights UI for makerig"""

import bpy
from ... import ClassManager
from ...services import LogService
from ...services import UiService
from ..abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("makerig.rigiopanel")

class MPFB_PT_MakeRigIO_Panel(Abstract_Panel):
    """MakeRig load/save rig and weights panel."""

    bl_label = "Load/Save rig"
    bl_category = UiService.get_value("RIGCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_MakeRig_Panel"

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        from ..makerig import MakeRigProperties

        rig_box = self._create_box(layout, "Load/Save rig", "TOOL_SETTINGS")
        MakeRigProperties.draw_properties(scene, rig_box, ["rig_parent", "rig_subrig", "rig_save_rigify", "rig_refit"])
        rig_box.operator("mpfb.load_rig")
        rig_box.operator("mpfb.save_rig")

        weights_box = self._create_box(layout, "Load/Save weights", "TOOL_SETTINGS")
        MakeRigProperties.draw_properties(scene, weights_box, ["weights_mask", "save_masks", "save_evaluated"])
        weights_box.operator("mpfb.load_weights")
        weights_box.operator("mpfb.save_weights")

ClassManager.add_class(MPFB_PT_MakeRigIO_Panel)
