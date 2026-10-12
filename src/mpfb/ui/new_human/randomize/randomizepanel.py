"""File containing the container UI panel for creating a randomized human."""

import os
from .... import ClassManager
from ....services import LogService
from ....services import UiService
from ....services import LocationService
from ....services import RandomizationService
from ...abstractpanel import Abstract_Panel
from .randomizeproperties import scene_to_spec, rebuild_preset_list

_LOG = LogService.get_logger("ui.new_human.randomize.randomizepanel")


class MPFB_PT_Randomize_Panel(Abstract_Panel):
    """Create a new human with a randomized phenotype.

    This is only the container; the actual settings live in the collapsible sub-panels below
    it (Presets, General settings, Macrodetails, Breast shape, Creation settings). Each of
    those sub-panels lives in its own module.
    """

    bl_label = "Random human"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_New_Panel"

    def draw(self, context):
        _LOG.enter()
        scene = context.scene

        # The default preset is written the first time the panel is drawn. This is kept on the
        # container panel so it runs regardless of which sub-panels are expanded.
        default_json = LocationService.get_user_config("randomization.default.json")
        if not os.path.exists(default_json):
            _LOG.info("The default randomization preset does not exist. Will create it.")
            RandomizationService.serialize_spec_to_json_file(scene_to_spec(scene), default_json)
            rebuild_preset_list()


ClassManager.add_class(MPFB_PT_Randomize_Panel)
