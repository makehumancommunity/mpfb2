"""File containing the general settings sub-panel of the randomize panel."""

from .... import ClassManager
from ....services import LogService
from ....services import UiService
from ...abstractpanel import Abstract_Panel
from .randomizeproperties import RANDOMIZE_PROPERTIES

_LOG = LogService.get_logger("ui.new_human.randomize.generalpanel")


class MPFB_PT_Randomize_General_Panel(Abstract_Panel):
    """Global randomization settings."""

    bl_label = "General settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Randomize_Panel"
    bl_order = 2

    def draw(self, context):
        _LOG.enter()
        scene = context.scene
        layout = self.layout
        RANDOMIZE_PROPERTIES.draw_properties(scene, layout, [
            "seed",
            "distribution"
            ])


ClassManager.add_class(MPFB_PT_Randomize_General_Panel)
