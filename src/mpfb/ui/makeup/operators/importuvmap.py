"""Operator for importing a UV map from a JSON file."""

import bpy
from bpy_extras.io_utils import ImportHelper
import json
from ....services import LogService
from ....services import MeshService
from ..makeuppanel import MAKEUP_PROPERTIES

from .... import ClassManager

_LOG = LogService.get_logger("makeup.importuvmap")


class MPFB_OT_ImportUvMapOperator(bpy.types.Operator, ImportHelper):
    """Import a UV map from a JSON file. Use the UV map data to create a new UV map on the active object,
    using the name set in MakeUp properties."""

    bl_idname = "mpfb.import_uv_map"
    bl_label = "Import UV map"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".json"

    @classmethod
    def poll(cls, context):
        """Check if the operator can run in the current context and that a mesh object is active."""
        return context.active_object is not None and context.active_object.type == 'MESH'

    def invoke(self, context, event):
        """Show the open file dialog."""
        return super().invoke(context, event)

    def execute(self, context):
        """Import the UV map from a JSON file."""
        mesh_object = context.active_object
        uv_map_name = MAKEUP_PROPERTIES.get_value("uv_map_name", entity_reference=context.scene)

        try:
            with open(self.filepath, 'r', encoding="utf-8") as json_file:
                uv_map_data = json.load(json_file)
        except Exception as excp:
            self.report({'ERROR'}, f"Failed to read UV map file: {excp}")
            return {'CANCELLED'}

        MeshService.add_uv_map_from_dict(mesh_object, uv_map_name, uv_map_data)

        self.report({'INFO'}, f"UV map '{uv_map_name}' imported from '{self.filepath}'.")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_ImportUvMapOperator)
