import os, bpy, shutil
from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.uiservice import UiService
from mpfb.services.objectservice import ObjectService
from mpfb.services.humanservice import HumanService
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("ui.humanpresetspanel")

_LOC = os.path.dirname(__file__)
HUMAN_PRESETS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
HUMAN_PRESETS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(HUMAN_PRESETS_PROPERTIES_DIR, prefix="HPR_")


def _populate_settings(self, context):
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
    return HumanService.get_list_of_human_presets(use_cache=False)

_SETTINGS_LIST_PROP = {
    "type": "enum",
    "name": "available_presets",
    "description": "These are the currently available saved humans",
    "label": "Available presets",
    "default": 0
}
HUMAN_PRESETS_PROPERTIES.add_property(_SETTINGS_LIST_PROP, _populate_settings)

class MPFB_PT_Human_Presets_Panel(Abstract_Panel):
    bl_label = "Human presets"
    bl_category = UiService.get_value("MATERIALSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Presets_Panel"

    def _load_save_box(self, scene, layout):
        _LOG.enter()
        HUMAN_PRESETS_PROPERTIES.draw_properties(scene, layout, ["available_presets"])
        layout.operator('mpfb.overwrite_human_presets')
        HUMAN_PRESETS_PROPERTIES.draw_properties(scene, layout, ["name"])
        layout.operator('mpfb.save_new_human_presets')

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        scene = context.scene

        self._load_save_box(scene, self._create_box(layout, "Load/save presets", "MODIFIER"))

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj:
            return False

        if ObjectService.object_is_basemesh_or_body_proxy(obj):
            return True

        if ObjectService.object_is_skeleton(obj):
            return True

        return False

ClassManager.add_class(MPFB_PT_Human_Presets_Panel)
