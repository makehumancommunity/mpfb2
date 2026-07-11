"""File containing the batch sub-panel of the randomize panel."""

from .... import ClassManager
from ....services import LogService
from ....services import UiService
from ...abstractpanel import Abstract_Panel
from .randomizeproperties import draw_batch

_LOG = LogService.get_logger("ui.new_human.randomize.batchpanel")


class MPFB_PT_Randomize_Batch_Panel(Abstract_Panel):
    """Batch generation of several randomized humans in one go."""

    bl_label = "Batch"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Randomize_Panel"
    bl_order = 10

    def draw(self, context):
        _LOG.enter()
        draw_batch(context.scene, self.layout)


ClassManager.add_class(MPFB_PT_Randomize_Batch_Panel)
