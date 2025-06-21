"""This file contains UI for working with makeup."""

from ... import ClassManager
from ...services import LocationService
from ...services import LogService
from ...services import MaterialService
from ...services import ObjectService
from ...services import UiService
from ...services import SceneConfigSet
from ..abstractpanel import Abstract_Panel
import os

_LOG = LogService.get_logger("ui.makeuppanel")

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

    sys_uv_layers_path = LocationService.get_mpfb_data("uv_layers")
    if os.path.exists(sys_uv_layers_path):
        for file_name in os.listdir(sys_uv_layers_path):
            _LOG.trace("file name", file_name)
            if file_name.endswith(".gz"):
                names.append(file_name)

    user_uv_layers_path = LocationService.get_user_data("uv_layers")
    if os.path.exists(user_uv_layers_path):
        for file_name in os.listdir(user_uv_layers_path):
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

_LAYER_LIST_PROP = {
    "type": "enum",
    "name": "layer_number",
    "description": "Which ink layer to write. If not explicitly set, the first ink layer will be used",
    "label": "Layer",
    "default": None
}


def _populate_layer(self, context):
    _LOG.enter()
    names = []

    mesh_object = context.active_object

    # Ensure the active object is a basemesh
    if not ObjectService.object_is_basemesh(mesh_object):
        return names

    material = MaterialService.get_material(mesh_object)
    if not material:
        return names

    if MaterialService.identify_material(material) != "makeskin":
        return names

    layers = MaterialService.get_number_of_ink_layers(material)

    if layers < 0:
        return names

    for i in range(layers):
        names.append((f"{i+1}", f"Ink layer {i+1}", f"Write ink  layer {i+1}", i))

    return names


MAKEUP_PROPERTIES.add_property(_LAYER_LIST_PROP, _populate_layer)


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

    def _write_ink_layer(self, scene, layout):
        """create_assets -> makeup -> write ink layer"""
        box = self.create_box(layout, "Write ink layer")
        MAKEUP_PROPERTIES.draw_properties(scene, box, ["layer_number", "ink_layer_name"])
        box.operator("mpfb.write_ink_layer")

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
        self._write_ink_layer(scene, layout)
        self._developer(scene, layout)


ClassManager.add_class(MPFB_PT_MakeUp_Panel)
