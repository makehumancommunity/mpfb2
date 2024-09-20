"""This file contains UI for working with makeup."""

from ... import ClassManager
from ...services import LocationService
from ...services import LogService
from ...services import UiService
from ...services import SceneConfigSet
from ..abstractpanel import Abstract_Panel
import os

_LOG = LogService.get_logger("ui.makeuppanel")
_LOG.set_level(LogService.DEBUG)

_LOC = os.path.dirname(__file__)
MAKEUP_PROPERTIES_DIR = os.path.join(_LOC, "properties")
MAKEUP_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(MAKEUP_PROPERTIES_DIR, prefix="MAKU_")

_FOCUS_LIST_PROP = {
    "type": "enum",
    "name": "focus_name",
    "description": "Which focus to add",
    "label": "Focus",
    "default": 0
}


def _populate_list(self, context):
    _LOG.enter()
    names = []
    for file_name in os.listdir(LocationService.get_mpfb_data("makeup")):
        _LOG.trace("file name", file_name)
        if file_name.endswith(".gz"):
            names.append(file_name)

    names.sort()

    list_index = 1
    output_list = [("NONE", "full body focus", "Do not use a specific UV map, instead use the default full body one", 0)]
    for name in names:
        list_name = str(name).replace(".json.gz", "").replace("_", " ")
        list_desc = "Use the specific UV map '" + list_name + "' for the ink layer"
        output_list.append((name, list_name, list_desc, list_index))
        list_index += 1

    return output_list


MAKEUP_PROPERTIES.add_property(_FOCUS_LIST_PROP, _populate_list)


class MPFB_PT_MakeUp_Panel(Abstract_Panel):
    """UI for various makeup related functions."""

    bl_label = "MakeUp"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("MATERIALSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Create_Panel"

    def _add_ink_layer(self, scene, layout):
        """create_assets -> makeup -> create ink layer"""
        box = self.create_box(layout, "Create ink layer")
        MAKEUP_PROPERTIES.draw_properties(scene, box, ["focus_name", "create_ink", "resolution"])
        box.operator("mpfb.create_ink")

    def _developer(self, scene, layout):
        """create_assets -> makeup -> developer"""
        box = self.create_box(layout, "MakeUP Developer")
        MAKEUP_PROPERTIES.draw_properties(scene, box, ["uv_map_name"])
        box.operator("mpfb.create_uv_map")
        box.operator("mpfb.write_uv_map")
        box.operator("mpfb.import_uv_map")

    def draw(self, context):
        """Draw the create_assets -> makeup panel hierarcy"""
        _LOG.enter()
        layout = self.layout
        scene = context.scene
        self._add_ink_layer(scene, layout)
        self._developer(scene, layout)


ClassManager.add_class(MPFB_PT_MakeUp_Panel)
