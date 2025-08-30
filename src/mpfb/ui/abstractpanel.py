"""File containing the base class for UI panels"""

import bpy
from ..services import LogService
from ..services import ObjectService
from ..services import TargetService
from ..services import UiService

_LOG = LogService.get_logger("ui.abstractpanel")

class Abstract_Panel(bpy.types.Panel):
    """Human modeling panel."""

    bl_label = "Abstract panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("DEVELOPERCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    def create_box(self, layout: bpy.types.UILayout, box_text: str, icon=None):
        _LOG.enter()
        box = layout.box()
        box.label(text=box_text)
        return box

    def _create_box(self, layout: bpy.types.UILayout, box_text: str, icon=None):
        return self.create_box(layout, box_text, icon)

    def get_basemesh(self, context, also_check_relatives=True):
        if context is None or context.active_object is None:
            return None
        basemesh = None

        if also_check_relatives:
            basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Basemesh")
        else:
            basemesh = context.active_object
            if not ObjectService.object_is_basemesh(basemesh):
                return None
        return basemesh

    @classmethod
    def active_object_is_basemesh(cls, context, also_check_relatives=False, also_check_for_shapekeys=False):
        if not context.active_object:
            return False
        if also_check_relatives:
            basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Basemesh")
        else:
            basemesh = context.active_object
            if not ObjectService.object_is_basemesh(basemesh):
                return False
        if not basemesh:
            return False
        if also_check_for_shapekeys:
            return TargetService.has_any_shapekey(basemesh)
        return True

