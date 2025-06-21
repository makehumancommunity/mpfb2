"""Operator for recomputing bone head or tail position from strategy."""
import bmesh
import bpy

from ....entities.rig import Rig
from ....services import LogService
from .... import ClassManager

from .abstract import AbstractBoneOperator

_LOG = LogService.get_logger("boneops.show_strategy_vertices")


class MPFB_OT_Show_Strategy_Vertices_Operator(AbstractBoneOperator):
    """Switch to mesh and select strategy vertices"""
    bl_idname = "mpfb.show_strategy_vertices"
    bl_label = "Show Strategy Vertices"

    # Because of https://developer.blender.org/T83649 Undo doesn't work for
    # strategy changes done in the Edit mode. Since undo during Edit is thus
    # pointless, this operator only pushes an undo stack record when switching
    # from the armature mode for the first time.
    #
    # The only way to revert edit mode changes is to undo all the way back to
    # before the switch from armature mode.

    select: bpy.props.BoolProperty(name="Select")
    is_tail: bpy.props.BoolProperty(name="Tail")
    index: bpy.props.IntProperty(name="Index")

    @classmethod
    def poll(cls, context):
        return isinstance(context.space_data, bpy.types.SpaceProperties) and cls.is_developer_bone(context)

    @classmethod
    def description(cls, _context, props):
        text = "Switch to the mesh"
        if props.select:
            text += " and select the vertices"
        return text

    def get_vertex_list(self, bone):
        info, _ = Rig.get_bone_end_strategy(bone, self.is_tail)

        if "vertex_indices" in info:
            indices = info["vertex_indices"]
            if self.index < 0:
                return indices
            elif 0 <= self.index <= len(indices):
                return [indices[self.index]]
        elif "vertex_index" in info:
            return [info["vertex_index"]]

        return None

    def execute(self, context):
        bone = self.get_bone(context)

        mesh_obj = self.get_vertex_mesh(bone)

        if not mesh_obj:
            return {'CANCELLED'}

        vertices = self.get_vertex_list(bone)

        if not self.switch_to_edit_mesh(context, mesh_obj):
            return {'FINISHED'}

        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

        if self.select:
            bpy.ops.mesh.select_all(action='DESELECT')

            if not vertices:
                self.report({'WARNING'}, "No vertices to select.")
            else:
                bm = bmesh.from_edit_mesh(mesh_obj.data)

                vertices = set(vertices)

                for i, v in enumerate(bm.verts):
                    if i in vertices:
                        v.hide_set(False)
                        v.select_set(True)
                        bm.select_history.add(v)

                bm.select_mode = {'VERT'}
                bm.select_flush_mode()

                bmesh.update_edit_mesh(mesh_obj.data, loop_triangles=False, destructive=False)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Show_Strategy_Vertices_Operator)
