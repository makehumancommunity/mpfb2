"""This file provides UI for saving/loading eye material settings"""

import os, bpy, shutil
from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.uiservice import UiService

_LOG = LogService.get_logger("ui.eyesettings")

_LOC = os.path.dirname(__file__)
EYE_SETTINGS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
EYE_SETTINGS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(EYE_SETTINGS_PROPERTIES_DIR, prefix="EYE_")


def _populate_settings(self, context):
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
    available_settings = UiService.get_eye_settings_panel_list()
    if available_settings is None:
        available_settings = []
    return available_settings

_SETTINGS_LIST_PROP = {
    "type": "enum",
    "name": "available_settings",
    "description": "Available settings",
    "label": "Available settings",
    "default": 0
}
EYE_SETTINGS_PROPERTIES.add_property(_SETTINGS_LIST_PROP, _populate_settings)

class MPFB_PT_Eye_Settings_Panel(bpy.types.Panel):
    """Panel for saving/loading eye material settings."""

    bl_label = "Eye material settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("MATERIALSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    def _create_box(self, layout, box_text, box_icon=None):
        _LOG.enter()
        box = layout.box()
        box.label(text=box_text, icon=box_icon)
        return box

    def _load_save_box(self, scene, layout):
        _LOG.enter()
        EYE_SETTINGS_PROPERTIES.draw_properties(scene, layout, ["available_settings"])
        layout.operator('mpfb.eyesettings_apply_settings')
        layout.operator('mpfb.overwrite_eye_settings')
        EYE_SETTINGS_PROPERTIES.draw_properties(scene, layout, ["name"])
        layout.operator('mpfb.save_new_eye_settings')

    def draw(self, context):
        _LOG.enter()

        ensure_eye_settings_default_exists()

        if UiService.get_eye_settings_panel_list() is None:
            UiService.rebuild_eye_settings_panel_list()

        layout = self.layout
        scene = context.scene

        self._load_save_box(scene, self._create_box(layout, "Load/save presets", "MODIFIER"))

def ensure_eye_settings_default_exists():
    """Check that the json file with the default eye settings exists in the user config dir.
    If not, copy it from the data directory."""
    _LOG.enter()
    default_json = LocationService.get_user_config("eye_settings.default.json")
    if not os.path.exists(default_json):
        _LOG.warn("The default eye settings do not exist. Will create at", default_json)
        template_settings = LocationService.get_mpfb_data("settings")
        default_json_template = os.path.join(template_settings, "eye_settings.default.json")
        if os.path.exists(default_json_template):
            _LOG.warn("Copying from", default_json_template)
            shutil.copy(default_json_template, default_json)
    else:
        _LOG.trace("Default eye settings exist")

ClassManager.add_class(MPFB_PT_Eye_Settings_Panel)
