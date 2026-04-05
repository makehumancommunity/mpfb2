"""Operator for removing weight info from a vertex group."""

import bpy
from pathlib import Path
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from .....services import LogService
from .....services import ObjectService
from ...makeweight.makeweightpanel import MAKEWEIGHT_PROPERTIES
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("makeweight.truncateweights")

@pollstrategy(PollStrategy.BASEMESH_ACTIVE)
class MPFB_OT_TruncateWeightsOperator(MpfbOperator):
    """Wipe all weight information from the selected vertex group"""
    bl_idname = "mpfb.truncate_weights"
    bl_label = "Truncate"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        from ....mpfbcontext import MpfbContext  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=MAKEWEIGHT_PROPERTIES)

        if not ctx.vertex_group:
            self.report({'ERROR'}, "A vertex group must be chosen")
            return {'FINISHED'}

        vertex_group = None
        for group in ctx.active_object.vertex_groups:
            if str(ctx.vertex_group).strip() == str(group.name).strip():
                vertex_group = group

        if not vertex_group:
            self.report({'ERROR'}, "Could not find the selected group")
            return {'FINISHED'}

        _LOG.dump("vertex_group", (vertex_group, vertex_group.index))

        vertices = []

        for vert in ctx.active_object.data.vertices:
            for group in vert.groups:
                if group.group == vertex_group.index:
                    vertices.append(vert.index)

        _LOG.dump("vertices", vertices)

        vertex_group.remove(vertices)

        self.report({'INFO'}, "Weights were removed")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_TruncateWeightsOperator)
