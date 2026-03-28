"""Operator for creating a UV map on a selected object."""

import bpy
from .....services import LogService
from ..makeuppanel import MAKEUP_PROPERTIES

from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy

_LOG = LogService.get_logger("makeup.createuvmap")


@pollstrategy(PollStrategy.ANY_MESH_OBJECT_ACTIVE)
class MPFB_OT_CreateUvMapOperator(bpy.types.Operator):
    """Create a new UV map on the selected object."""

    bl_idname = "mpfb.create_uv_map"
    bl_label = "Create UV map"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Create a new UV map on the selected object, using the name set in the Makeup Properties."""
        mesh_object = context.active_object
        uv_map_name = MAKEUP_PROPERTIES.get_value("uv_map_name", entity_reference=context.scene)

        if uv_map_name in mesh_object.data.uv_layers:
            self.report({'WARNING'}, f"UV map '{uv_map_name}' already exists.")
            return {'CANCELLED'}

        mesh_object.data.uv_layers.new(name=uv_map_name)
        self.report({'INFO'}, f"UV map '{uv_map_name}' created.")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_CreateUvMapOperator)
