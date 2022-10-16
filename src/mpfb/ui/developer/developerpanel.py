"""This file contains the developer panel."""

from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet
import bpy, os

_LOG = LogService.get_logger("ui.developerpanel")

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
DEVELOPER_PROPERTIES_DIR = os.path.join(_LOC, "properties")
DEVELOPER_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(DEVELOPER_PROPERTIES_DIR, prefix="DEV_")
DEVELOPER_PROPERTIES.add_property(_LEVELS_LIST_PROP, _populate_list)

class MPFB_PT_Developer_Panel(bpy.types.Panel):
    """UI for various developer functions."""
    bl_label = "Developer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("DEVELOPERCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    def _create_box(self, layout, box_text):
        _LOG.enter()
        box = layout.box()
        box.label(text=box_text)
        return box

    def _log_levels(self, scene, layout):
        box = self._create_box(layout, "Log levels")
        box.operator("mpfb.list_log_levels")
        box.operator("mpfb.reset_log_levels")
        DEVELOPER_PROPERTIES.draw_properties(scene, box, ["available_loggers", "chosen_level"])
        box.operator("mpfb.set_log_level")

    def _export_log_file(self, scene, layout):
        box = self._create_box(layout, "Export log file")
        box.label(text="Use default for combined log")
        DEVELOPER_PROPERTIES.draw_properties(scene, box, ["available_loggers"])
        box.operator("mpfb.export_log")

    def _nodes(self, layout):
        box = self._create_box(layout, "Load/save nodes")
        box.operator("mpfb.save_nodes")
        box.operator("mpfb.load_nodes")

    def _rig(self, scene, layout):
        box = self._create_box(layout, "Load/Save rig")
        DEVELOPER_PROPERTIES.draw_properties(scene, box, ["rig_parent"])
        box.operator("mpfb.load_rig")
        box.operator("mpfb.save_rig")
        box.operator("mpfb.load_rigify_layers")
        box.operator("mpfb.save_rigify_layers")

    def _weights(self, scene, layout):
        box = self._create_box(layout, "Load/Save weights")
        DEVELOPER_PROPERTIES.draw_properties(scene, box, ["save_evaluated"])
        box.operator("mpfb.load_weights")
        box.operator("mpfb.save_weights")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene
        self._log_levels(scene, layout)
        self._export_log_file(scene, layout)
        self._nodes(layout)
        self._rig(scene, layout)
        self._weights(scene, layout)


ClassManager.add_class(MPFB_PT_Developer_Panel)

