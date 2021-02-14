
import os, bpy, shutil
from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.uiservice import UiService

_LOG = LogService.get_logger("ui.enhancedsettings")

_LOC = os.path.dirname(__file__)
ENHANCED_SETTINGS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
ENHANCED_SETTINGS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(ENHANCED_SETTINGS_PROPERTIES_DIR, prefix="ES_")


def _populate_settings(self, context):
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
    available_settings = UiService.get_enhanced_settings_panel_list()
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
ENHANCED_SETTINGS_PROPERTIES.add_property(_SETTINGS_LIST_PROP, _populate_settings)

class MPFB_PT_Enhanced_Settings_Panel(bpy.types.Panel):
    bl_label = "Enhanced material settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("MATERIALSCATEGORY")

    def _create_box(self, layout, box_text, box_icon=None):
        _LOG.enter()
        box = layout.box()
        box.label(text=box_text, icon=box_icon)
        return box

    def _load_save_box(self, scene, layout):
        _LOG.enter()
        ENHANCED_SETTINGS_PROPERTIES.draw_properties(scene, layout, ["available_settings"])
        layout.operator('mpfb.enhancedsettings_apply_settings')
        layout.operator('mpfb.overwrite_enhanced_settings')
        ENHANCED_SETTINGS_PROPERTIES.draw_properties(scene, layout, ["name"])
        layout.operator('mpfb.save_new_enhanced_settings')

    def draw(self, context):
        _LOG.enter()

        # TODO: this section should probably also be present in the importer panel
        default_json = LocationService.get_user_config("enhanced_settings.default.json")
        if not os.path.exists(default_json):
            _LOG.warn("The default enhanced settings do not exist. Will create at", default_json)
            template_settings = LocationService.get_mpfb_data("settings")
            default_json_template = os.path.join(template_settings, "enhanced_settings.default.json")
            _LOG.warn("Copying from", default_json_template)
            shutil.copy(default_json_template, default_json)
        else:
            _LOG.trace("Default enhanced settings exist")

        if UiService.get_enhanced_settings_panel_list() is None:
            UiService.rebuild_enhanced_settings_panel_list()

        layout = self.layout
        scene = context.scene

        self._load_save_box(scene, self._create_box(layout, "Load/save presets", "MODIFIER"))


ClassManager.add_class(MPFB_PT_Enhanced_Settings_Panel)
