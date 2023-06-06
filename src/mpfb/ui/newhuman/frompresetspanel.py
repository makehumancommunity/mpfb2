"""File containing main UI for creating humans from presets"""

import bpy, os
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.humanservice import HumanService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("newhuman.frompresetspanel")

_LOC = os.path.dirname(__file__)
PRESETS_HUMAN_PROPERTIES_DIR = os.path.join(_LOC, "properties")
PRESETS_HUMAN_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(PRESETS_HUMAN_PROPERTIES_DIR, prefix="FPR_")

def _populate_settings(self, context):
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
    return HumanService.get_list_of_human_presets(use_cache=False)

_SETTINGS_LIST_PROP = {
    "type": "enum",
    "name": "available_presets",
    "description": "These are the currently available saved humans. You can additional humans to this list on the \"manage presets\" panel",
    "label": "Preset",
    "default": None
}
PRESETS_HUMAN_PROPERTIES.add_property(_SETTINGS_LIST_PROP, _populate_settings)

class MPFB_PT_From_Presets_Panel(Abstract_Panel):
    """Create human from preset main panel."""

    bl_label = "From presets"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_New_Panel"

    def _create(self, scene, layout):
        PRESETS_HUMAN_PROPERTIES.draw_properties(scene, layout, [
            "available_presets",
            "scale_factor",
            "override_rig",
            "override_skin_model",
            "detailed_helpers",
            "extra_vertex_groups",
            "mask_helpers",
            "load_clothes",
            "bodypart_deep_search",
            "clothes_deep_search"
            ])
        layout.operator('mpfb.human_from_presets')
        layout.operator('mpfb.human_from_mhm')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene
        self._create(scene, layout)


ClassManager.add_class(MPFB_PT_From_Presets_Panel)


