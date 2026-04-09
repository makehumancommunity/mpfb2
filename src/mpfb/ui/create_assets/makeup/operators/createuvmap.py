"""Operator for creating a UV map on a selected object."""

import bpy
from .....services import LogService
from ..makeuppanel import MAKEUP_PROPERTIES

from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext

_LOG = LogService.get_logger("makeup.createuvmap")

@pollstrategy(PollStrategy.ANY_MESH_OBJECT_ACTIVE)
class MPFB_OT_CreateUvMapOperator(MpfbOperator):
    """Create a new UV map on the selected object."""

    bl_idname = "mpfb.create_uv_map"
    bl_label = "Create UV map"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        """Create a new UV map on the selected object, using the name set in the Makeup Properties."""

        ctx = MpfbContext(context=context, scene_properties=MAKEUP_PROPERTIES)

        if ctx.uv_map_name in ctx.active_object.data.uv_layers:
            self.report({'WARNING'}, f"UV map '{ctx.uv_map_name}' already exists.")
            return {'CANCELLED'}

        ctx.active_object.data.uv_layers.new(name=ctx.uv_map_name)
        self.report({'INFO'}, f"UV map '{ctx.uv_map_name}' created.")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_CreateUvMapOperator)
