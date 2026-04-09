"""Operator for importing a UV map from a JSON file."""

import bpy
from bpy_extras.io_utils import ImportHelper
import json
from .....services import LogService
from .....services import MeshService
from ..makeuppanel import MAKEUP_PROPERTIES

from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext

_LOG = LogService.get_logger("makeup.importuvmap")

@pollstrategy(PollStrategy.ANY_MESH_OBJECT_ACTIVE)
class MPFB_OT_ImportUvMapOperator(MpfbOperator, ImportHelper):
    """Import a UV map from a JSON file. Use the UV map data to create a new UV map on the active object,
    using the name set in MakeUp properties."""

    bl_idname = "mpfb.import_uv_map"
    bl_label = "Import UV map"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".json"

    def get_logger(self):
        return _LOG

    def invoke(self, context, event):
        """Show the open file dialog."""
        return super().invoke(context, event)

    def hardened_execute(self, context):
        """Import the UV map from a JSON file."""

        ctx = MpfbContext(context=context, scene_properties=MAKEUP_PROPERTIES)

        try:
            with open(self.filepath, 'r', encoding="utf-8") as json_file:
                uv_map_data = json.load(json_file)
        except Exception as excp:
            self.report({'ERROR'}, f"Failed to read UV map file: {excp}")
            return {'CANCELLED'}

        MeshService.add_uv_map_from_dict(ctx.active_object, ctx.uv_map_name, uv_map_data)

        self.report({'INFO'}, f"UV map '{ctx.uv_map_name}' imported from '{self.filepath}'.")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ImportUvMapOperator)
