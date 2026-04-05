"""Operator for writing a UV map to a JSON file."""

import bpy
from bpy_extras.io_utils import ExportHelper
import json
from .....services import LogService
from .....services import MeshService
from ..makeuppanel import MAKEUP_PROPERTIES

from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("makeup.writeuvmap")


@pollstrategy(PollStrategy.ANY_MESH_OBJECT_ACTIVE)
class MPFB_OT_WriteUvMapOperator(MpfbOperator, ExportHelper):
    """Write a UV map to a JSON file. If there are multiple UV maps on the active object, use the one which matches
    the name set in the Makeup Properties. If no match is found, use active UV map."""

    bl_idname = "mpfb.write_uv_map"
    bl_label = "Write UV map"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".json"

    def get_logger(self):
        return _LOG

    def invoke(self, context, event):
        """Show the save file dialog."""
        name = MAKEUP_PROPERTIES.get_value("uv_map_name", entity_reference=context.scene)
        self.filepath = bpy.path.clean_name(name, replace="-") + ".json"
        return super().invoke(context, event)

    def hardened_execute(self, context):
        """Write the UV map to a JSON file."""
        from ....mpfbcontext import MpfbContext  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=MAKEUP_PROPERTIES)

        # Check that the mesh object has a vertex group called exactly "uvmap".
        if not ctx.active_object.vertex_groups.get("uvmap"):
            self.report({'ERROR'}, "The mesh object does not have a vertex group called 'uvmap'.")
            return {'CANCELLED'}

        uv_layer = ctx.active_object.data.uv_layers.get(ctx.uv_map_name)
        if uv_layer is None:
            uv_layer = ctx.active_object.data.uv_layers.active

        if uv_layer is None:
            self.report({'ERROR'}, "No UV map found.")
            return {'CANCELLED'}

        uv_map_data = MeshService.get_uv_map_as_dict(ctx.active_object, uv_layer.name, only_include_vertex_group="uvmap")

        with open(self.filepath, 'w', encoding="utf-8") as json_file:
            json.dump(uv_map_data, json_file, indent=4)

        self.report({'INFO'}, f"UV map '{uv_layer.name}' written to '{self.filepath}'.")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_WriteUvMapOperator)
