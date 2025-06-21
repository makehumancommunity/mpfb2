"""This file contains the developer panel."""

from ... import ClassManager
from ...services import LogService
from ...services import UiService
from ...services import SceneConfigSet
import bpy, os

_LOG = LogService.get_logger("ui.developerpanel")

def invalidate_list():
    """In order to force a reload of the available loggers. This shouldn't really be needed."""
    pass

def _populate_list(self, context):
    _LOG.enter()
    global DEVELOPER_PROPERTIES # pylint: disable=W0603
    filter=""
    if isinstance(context, bpy.types.Scene):
        filter = DEVELOPER_PROPERTIES.get_value("loggers_filter", entity_reference=context)
    else:
        filter = DEVELOPER_PROPERTIES.get_value("loggers_filter", entity_reference=context.scene)
    return LogService.get_loggers_list_as_property_enum(filter)

def _populate_categories(self, context):
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
    return LogService.get_loggers_categories_as_property_enum()

_LEVELS_LIST_PROP = {
    "type": "enum",
    "name": "available_loggers",
    "description": "Available loggers",
    "label": "Available loggers",
    "default": None
}

_LOGGERS_FILTER_PROP = {
    "type": "enum",
    "name": "loggers_filter",
    "description": "Only list loggers starting with this string",
    "label": "Filter loggers",
    "default": None
}

_LOC = os.path.dirname(__file__)
DEVELOPER_PROPERTIES_DIR = os.path.join(_LOC, "properties")
DEVELOPER_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(DEVELOPER_PROPERTIES_DIR, prefix="DEV_")
DEVELOPER_PROPERTIES.add_property(_LEVELS_LIST_PROP, _populate_list)
DEVELOPER_PROPERTIES.add_property(_LOGGERS_FILTER_PROP, _populate_categories)

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
        DEVELOPER_PROPERTIES.draw_properties(scene, box, ["loggers_filter", "available_loggers", "chosen_level"])
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
        box.operator("mpfb.rewrite_node_types")

    def _rig(self, scene, layout):
        box = self._create_box(layout, "Load/Save rig")
        DEVELOPER_PROPERTIES.draw_properties(scene, box, ["rig_parent", "rig_subrig", "rig_save_rigify", "rig_refit"])
        box.operator("mpfb.load_rig")
        box.operator("mpfb.save_rig")

    def _weights(self, scene, layout):
        box = self._create_box(layout, "Load/Save weights")
        DEVELOPER_PROPERTIES.draw_properties(scene, box, ["weights_mask", "save_masks", "save_evaluated"])
        box.operator("mpfb.load_weights")
        box.operator("mpfb.save_weights")

    def _targets(self, scene, layout):
        box = self._create_box(layout, "Load/Save targets")
        box.operator("mpfb.load_target")
        box.operator("mpfb.save_target")

    def _tests(self, scene, layout):
        box = self._create_box(layout, "Unit tests")
        box.label(text="See README in test dir")
        box.operator("mpfb.unit_tests")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene
        self._log_levels(scene, layout)
        self._export_log_file(scene, layout)
        self._nodes(layout)
        self._rig(scene, layout)
        self._weights(scene, layout)
        self._targets(scene, layout)
        self._tests(scene, layout)


ClassManager.add_class(MPFB_PT_Developer_Panel)

