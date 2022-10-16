"""This file contains the developer panel for the node editor."""

from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.ui.abstractpanel import Abstract_Panel
import bpy, os

_LOG = LogService.get_logger("ui.nodedeveloperpanel")

#===============================================================================
# _NEED_RELOAD = True
# _CACHED_LEVELS_LIST = []
#
# def invalidate_list():
#     """In order to force a reload of the available loggers. This shouldn't really be needed."""
#     global _NEED_RELOAD # pylint: disable=W0603
#     _NEED_RELOAD = True
#
# def _populate_list(self, context):
#     global _NEED_RELOAD # pylint: disable=W0603
#     global _CACHED_LEVELS_LIST # pylint: disable=W0603
#     _LOG.enter()
#     _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
#     if _NEED_RELOAD:
#         _CACHED_LEVELS_LIST = LogService.get_loggers_list_as_property_enum()
#         _NEED_RELOAD = False
#     return _CACHED_LEVELS_LIST
#
# _LEVELS_LIST_PROP = {
#     "type": "enum",
#     "name": "available_loggers",
#     "description": "Available loggers",
#     "label": "Available loggers",
#     "default": 0
# }
#
# _LOC = os.path.dirname(__file__)
# DEVELOPER_PROPERTIES_DIR = os.path.join(_LOC, "properties")
# DEVELOPER_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(DEVELOPER_PROPERTIES_DIR, prefix="DEV_")
# DEVELOPER_PROPERTIES.add_property(_LEVELS_LIST_PROP, _populate_list)
#===============================================================================

class MPFB_PT_Node_Developer_Panel(Abstract_Panel):
    """UI for various node developer functions."""
    bl_idname = "NODE_PT_mpfb_node_developer_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_label = "Node developer"
    bl_region_type = "UI"
    bl_category = UiService.get_value("DEVELOPERCATEGORY")

    def _nodes(self, layout):
        box = self._create_box(layout, "Dump nodes")
        box.operator("mpfb.print_node_group")
        #box.operator("mpfb.load_nodes")

    @classmethod
    def poll(self, context):
        return context.area.ui_type == "ShaderNodeTree"

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        _LOG.debug("Context", context)
        scene = context.scene
        _LOG.debug("Scene", scene)
        node_tree = context.space_data.node_tree
        _LOG.debug("Node tree", node_tree)

        selected = context.selected_nodes
        _LOG.debug("Selected", selected)

        self._nodes(layout)

ClassManager.add_class(MPFB_PT_Node_Developer_Panel)

