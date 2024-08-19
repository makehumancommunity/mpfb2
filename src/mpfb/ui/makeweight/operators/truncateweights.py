"""Operator for removing weight info from a vertex group."""

import bpy
from pathlib import Path
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from ....services import LogService
from ....services import ObjectService
from ...makeweight.makeweightpanel import MAKEWEIGHT_PROPERTIES
from mpfb import ClassManager

_LOG = LogService.get_logger("makeweight.truncateweights")

class MPFB_OT_TruncateWeightsOperator(bpy.types.Operator):
    """Wipe all weight information from the selected vertex group"""
    bl_idname = "mpfb.truncate_weights"
    bl_label = "Truncate"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return ObjectService.object_is_basemesh(context.active_object)

    def execute(self, context):

        blender_object = context.active_object

        group_name = MAKEWEIGHT_PROPERTIES.get_value("vertex_group", entity_reference=context.scene)
        if not group_name:
            self.report({'ERROR'}, "A vertex group must be chosen")
            return {'FINISHED'}

        vertex_group = None
        for group in blender_object.vertex_groups:
            if str(group_name).strip() == str(group.name).strip():
                vertex_group = group

        if not vertex_group:
            self.report({'ERROR'}, "Could not find the selected group")
            return {'FINISHED'}

        _LOG.dump("vertex_group", (vertex_group, vertex_group.index))

        vertices = []

        for vert in blender_object.data.vertices:
            for group in vert.groups:
                if group.group == vertex_group.index:
                    vertices.append(vert.index)

        _LOG.dump("vertices", vertices)

        vertex_group.remove(vertices)

        self.report({'INFO'}, "Weights were removed")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_TruncateWeightsOperator)
