"""File containing the macrodetails sub-panel of the randomize panel."""

from .... import ClassManager
from ....services import LogService
from ....services import UiService
from ...abstractpanel import Abstract_Panel
from .randomizeproperties import _ATTRIBUTE_GROUPS, draw_attribute_group, draw_race_box

_LOG = LogService.get_logger("ui.new_human.randomize.macrodetailspanel")


class MPFB_PT_Randomize_Macrodetails_Panel(Abstract_Panel):
    """Randomization settings for the macrodetail attributes and race."""

    bl_label = "Macrodetails"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Randomize_Panel"
    bl_order = 3

    def draw(self, context):
        _LOG.enter()
        scene = context.scene
        layout = self.layout
        draw_attribute_group(scene, layout, _ATTRIBUTE_GROUPS[0][1])
        # Race is drawn in its own labelled box, alongside the other macrodetail boxes.
        draw_race_box(scene, layout)


ClassManager.add_class(MPFB_PT_Randomize_Macrodetails_Panel)
