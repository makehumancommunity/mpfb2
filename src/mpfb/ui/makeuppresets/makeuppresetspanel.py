"""Panel for managing makeup presets"""

import os, bpy
from ... import ClassManager
from ...services import LogService
from ...services import LocationService
from ...services import SceneConfigSet
from ...services import UiService
from ..abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("ui.makeuppresetspanel")

_LOC = os.path.dirname(__file__)
MAKEUP_PRESETS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
MAKEUP_PRESETS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(MAKEUP_PRESETS_PROPERTIES_DIR, prefix="MUPR_")


def _populate_settings(self, context):
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))

    confdir = LocationService.get_user_config()
    makeups = []
    for file in os.listdir(confdir):
        if file.endswith(".json") and file.startswith("makeup."):
            makeups.append(str(file).split(".")[1])
    makeups.sort()
    presets = []
    current_id = 0
    for name in makeups:
        presets.append((name, name, "the " + name + " makeup", current_id))
        current_id = current_id + 1
    return presets


_SETTINGS_LIST_PROP = {
    "type": "enum",
    "name": "available_presets",
    "description": "These are the currently available saved makeups",
    "label": "Available makeups",
    "default": 0
}
MAKEUP_PRESETS_PROPERTIES.add_property(_SETTINGS_LIST_PROP, _populate_settings)


class MPFB_PT_Makeup_Presets_Panel(Abstract_Panel):
    """Panel for managing makeup presets."""

    bl_label = "Makeup presets"
    bl_category = UiService.get_value("MATERIALSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Presets_Panel"

    def _load_save_box(self, scene, layout):
        _LOG.enter()
        MAKEUP_PRESETS_PROPERTIES.draw_properties(scene, layout, ["available_presets"])
        layout.operator('mpfb.load_makeup_presets')
        layout.operator('mpfb.overwrite_makeup_presets')
        MAKEUP_PRESETS_PROPERTIES.draw_properties(scene, layout, ["name"])
        layout.operator('mpfb.save_new_makeup_presets')

    def draw(self, context):
        """Draw the load/save presets panel"""
        _LOG.enter()

        layout = self.layout
        scene = context.scene

        self._load_save_box(scene, self._create_box(layout, "Load/save presets", "MODIFIER"))

    @classmethod
    def poll(cls, context):
        """Poll for the availability of the panel"""
        obj = context.active_object
        if not obj:
            return False

        return True


ClassManager.add_class(MPFB_PT_Makeup_Presets_Panel)
