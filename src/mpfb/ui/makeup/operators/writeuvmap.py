"""Operator for writing a UV map to a JSON file."""

import bpy
from bpy_extras.io_utils import ExportHelper
import json
from ....services import LogService
from ....services import MeshService
from ..makeuppanel import MAKEUP_PROPERTIES

from .... import ClassManager

_LOG = LogService.get_logger("makeup.writeuvmap")


class MPFB_OT_WriteUvMapOperator(bpy.types.Operator, ExportHelper):
    """Write a UV map to a JSON file. If there are multiple UV maps on the active object, use the one which matches
    the name set in the Makeup Properties. If no match is found, use active UV map."""

    bl_idname = "mpfb.write_uv_map"
    bl_label = "Write UV map"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".json"

    @classmethod
    def poll(cls, context):
        """Check if the operator can run in the current context and that a mesh object is active."""
        return context.active_object is not None and context.active_object.type == 'MESH'

    def invoke(self, context, event):
        """Show the save file dialog."""
        name = MAKEUP_PROPERTIES.get_value("uv_map_name", entity_reference=context.scene)
        self.filepath = bpy.path.clean_name(name, replace="-") + ".json"
        return super().invoke(context, event)

    def execute(self, context):
        """Write the UV map to a JSON file."""
        mesh_object = context.active_object

        # Check that the mesh object has a vertex group called exactly "uvmap".
        if not mesh_object.vertex_groups.get("uvmap"):
            self.report({'ERROR'}, "The mesh object does not have a vertex group called 'uvmap'.")
            return {'CANCELLED'}

        uv_map_name = MAKEUP_PROPERTIES.get_value("uv_map_name", entity_reference=context.scene)

        uv_layer = mesh_object.data.uv_layers.get(uv_map_name)
        if uv_layer is None:
            uv_layer = mesh_object.data.uv_layers.active

        if uv_layer is None:
            self.report({'ERROR'}, "No UV map found.")
            return {'CANCELLED'}

        uv_map_data = MeshService.get_uv_map_as_dict(mesh_object, uv_layer.name, only_include_vertex_group="uvmap")

        with open(self.filepath, 'w', encoding="utf-8") as json_file:
            json.dump(uv_map_data, json_file, indent=4)

        self.report({'INFO'}, f"UV map '{uv_layer.name}' written to '{self.filepath}'.")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_WriteUvMapOperator)
