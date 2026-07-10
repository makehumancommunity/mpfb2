"""File containing the clothes sub-panel of the randomize panel."""

from .... import ClassManager
from ....services import LogService
from ....services import UiService
from ...abstractpanel import Abstract_Panel
from .randomizeproperties import draw_clothes

_LOG = LogService.get_logger("ui.new_human.randomize.clothespanel")


class MPFB_PT_Randomize_Clothes_Panel(Abstract_Panel):
    """Randomization settings for clothes, with one collapsible box per body slot."""

    bl_label = "Clothes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Randomize_Panel"
    bl_order = 7

    def draw(self, context):
        _LOG.enter()
        draw_clothes(context.scene, self.layout)


ClassManager.add_class(MPFB_PT_Randomize_Clothes_Panel)
