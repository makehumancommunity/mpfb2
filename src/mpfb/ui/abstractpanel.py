"""File containing the base class for UI panels"""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService

_LOG = LogService.get_logger("ui.abstractpanel")

class Abstract_Panel(bpy.types.Panel):
    """Human modeling panel."""

    bl_label = "Abstract panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("DEVELOPERCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    def create_box(self, layout, box_text, icon=None):
        _LOG.enter()
        box = layout.box()
        box.label(text=box_text)
        return box

    def _create_box(self, layout, box_text, icon=None):
        return self.create_box(layout, box_text, icon)
