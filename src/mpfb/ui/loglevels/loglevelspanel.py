"""This file contains the log levels panel."""

from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet
import bpy, os

_LOG = LogService.get_logger("ui.loglevelspanel")

_NEED_RELOAD = True
_CACHED_LEVELS_LIST = []

def invalidate_list():
    """In order to force a reload of the available loggers. This shouldn't really be needed."""
    global _NEED_RELOAD # pylint: disable=W0603
    _NEED_RELOAD = True

def _populate_list(self, context):
    global _NEED_RELOAD # pylint: disable=W0603
    global _CACHED_LEVELS_LIST # pylint: disable=W0603
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
    if _NEED_RELOAD:
        _CACHED_LEVELS_LIST = LogService.get_loggers_list_as_property_enum()
        _NEED_RELOAD = False
    return _CACHED_LEVELS_LIST

_LEVELS_LIST_PROP = {
    "type": "enum",
    "name": "available_loggers",
    "description": "Available loggers",
    "label": "Available loggers",
    "default": 0
}

_LOC = os.path.dirname(__file__)
LOG_LEVELS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
LOG_LEVELS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(LOG_LEVELS_PROPERTIES_DIR, prefix="LL_")
LOG_LEVELS_PROPERTIES.add_property(_LEVELS_LIST_PROP, _populate_list)

class MPFB_PT_Log_Levels_Panel(bpy.types.Panel):
    """The main UI for controlling log levels."""
    bl_label = "Log levels"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("DEVELOPERCATEGORY")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene
        layout.operator("mpfb.list_log_levels")
        layout.operator("mpfb.reset_log_levels")
        LOG_LEVELS_PROPERTIES.draw_properties(scene, layout, ["available_loggers", "chosen_level"])
        layout.operator("mpfb.set_log_level")

ClassManager.add_class(MPFB_PT_Log_Levels_Panel)

