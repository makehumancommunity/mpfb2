"""File containing the skin sub-panel of the randomize panel."""

from .... import ClassManager
from ....services import LogService
from ....services import UiService
from ...abstractpanel import Abstract_Panel
from .randomizeproperties import RANDOMIZE_PROPERTIES

_LOG = LogService.get_logger("ui.new_human.randomize.skinpanel")


class MPFB_PT_Randomize_Skin_Panel(Abstract_Panel):
    """Randomization settings for the skin material."""

    bl_label = "Skin"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Randomize_Panel"
    bl_order = 5

    def draw(self, context):
        _LOG.enter()
        scene = context.scene
        layout = self.layout
        RANDOMIZE_PROPERTIES.draw_properties(scene, layout, [
            "randomize_skin",
            "match_gender",
            "match_age",
            "match_race",
            "skin_fallback",
            "skin_pack",
            "skin_include",
            "skin_exclude",
            "skin_type",
            "skin_material_instances"
            ])


ClassManager.add_class(MPFB_PT_Randomize_Skin_Panel)
