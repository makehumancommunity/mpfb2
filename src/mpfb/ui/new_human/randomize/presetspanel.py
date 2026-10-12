"""File containing the presets sub-panel of the randomize panel."""

from .... import ClassManager
from ....services import LogService
from ....services import UiService
from ...abstractpanel import Abstract_Panel
from .randomizeproperties import RANDOMIZE_PROPERTIES

_LOG = LogService.get_logger("ui.new_human.randomize.presetspanel")


class MPFB_PT_Randomize_Presets_Panel(Abstract_Panel):
    """Save and load randomization presets."""

    bl_label = "Presets"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = set()
    bl_parent_id = "MPFB_PT_Randomize_Panel"
    bl_order = 1

    def draw(self, context):
        _LOG.enter()
        scene = context.scene
        layout = self.layout
        RANDOMIZE_PROPERTIES.draw_properties(scene, layout, ["available_presets"])
        layout.operator('mpfb.randomize_load_preset')
        layout.operator('mpfb.randomize_overwrite_preset')
        RANDOMIZE_PROPERTIES.draw_properties(scene, layout, ["name"])
        layout.operator('mpfb.randomize_save_new_preset')


ClassManager.add_class(MPFB_PT_Randomize_Presets_Panel)
