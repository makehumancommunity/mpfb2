
import os, bpy
from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.uiservice import UiService

_LOG = LogService.get_logger("importer.importerpanel")

_LOC = os.path.dirname(__file__)
IMPORTER_PROPERTIES_DIR = os.path.join(_LOC, "properties")
IMPORTER_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(IMPORTER_PROPERTIES_DIR, prefix="IMP_")


def _populate_presets(self, context):
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
    available_presets = UiService.get_importer_panel_list()
    if available_presets is None:
        available_presets = []
    return available_presets

def _populate_skin_settings(self, context):
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
    available_settings = UiService.get_importer_enhanced_settings_panel_list()
    if available_settings is None:
        available_settings = []
    return available_settings

def _populate_eye_settings(self, context):
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
    available_settings = UiService.get_importer_eye_settings_panel_list()
    if available_settings is None:
        available_settings = []
    return available_settings


_PRESETS_LIST_PROP = {
    "type": "enum",
    "name": "presets_for_import",
    "description": "Presets to use when importing a human",
    "label": "Presets to use",
    "default": 0
}
IMPORTER_PROPERTIES.add_property(_PRESETS_LIST_PROP, _populate_presets)

_SKIN_SETTINGS_LIST_PROP = {
    "type": "enum",
    "name": "skin_settings_for_import",
    "description": "Skin material settings to use when importing a human. These are created on the material tab.",
    "label": "Skin settings to use",
    "default": 0
}
IMPORTER_PROPERTIES.add_property(_SKIN_SETTINGS_LIST_PROP, _populate_skin_settings)

_EYE_SETTINGS_LIST_PROP = {
    "type": "enum",
    "name": "eye_settings_for_import",
    "description": "Eye material settings to use when importing a human. These are created on the material tab.",
    "label": "Eye settings to use",
    "default": 0
}
IMPORTER_PROPERTIES.add_property(_EYE_SETTINGS_LIST_PROP, _populate_skin_settings)

UiService.set_value("importer_properties", IMPORTER_PROPERTIES)

class MPFB_PT_Importer_Panel(bpy.types.Panel):
    bl_label = "Import from MakeHuman"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("IMPORTERCATEGORY")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scn = context.scene

        from mpfb.ui.eyesettings.eyesettingspanel import ensure_eye_settings_default_exists
        ensure_eye_settings_default_exists()

        if UiService.get_importer_panel_list() is None:
            UiService.rebuild_importer_panel_list()
        if UiService.get_importer_enhanced_settings_panel_list() is None:
            UiService.rebuild_importer_enhanced_settings_panel_list();
        if UiService.get_importer_eye_settings_panel_list() is None:
            UiService.rebuild_importer_eye_settings_panel_list();

        IMPORTER_PROPERTIES.draw_properties(scn, layout, [
            "presets_for_import",
            "skin_settings_for_import",
            "eye_settings_for_import"
            ])
        layout.operator('mpfb.importer_import_body')


ClassManager.add_class(MPFB_PT_Importer_Panel)
