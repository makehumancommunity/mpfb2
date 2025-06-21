"""Operator for recomputing bone head or tail position from strategy."""
import bmesh
import bpy

from ....entities.rig import Rig
from ....services import LogService
from .... import ClassManager

from .abstract import AbstractBoneOperator

_LOG = LogService.get_logger("boneops.save_strategy_vertices")


class MPFB_OT_Save_Strategy_Vertices_Operator(AbstractBoneOperator):
    """Save selected vertices to strategy"""
    bl_idname = "mpfb.save_strategy_vertices"
    bl_label = "Save Vertices"

    # Because of https://developer.blender.org/T83649 Undo doesn't work for
    # strategy changes done in the Edit mode. Since undo during Edit is thus
    # pointless, this operator only pushes an undo stack record when returning
    # to armature mode, while switch=False produces no undo.
    #
    # The only way to revert edit mode changes is to undo all the way back to
    # before the switch from armature mode.

    switch: bpy.props.BoolProperty(name="Switch", default=False)
    save: bpy.props.BoolProperty(name="Save", default=True)
    is_tail: bpy.props.BoolProperty(name="Tail")
    index: bpy.props.IntProperty(name="Index")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == "MESH" and obj.mode == "EDIT" and
                isinstance(context.space_data, bpy.types.SpaceProperties) and
                cls.is_developer_bone(context))

    @classmethod
    def description(cls, _context, props):
        text = []
        if props.save:
            text.append("save the selected vertices to strategy")
        if props.switch:
            text.append("switch to editing the armature")
        if text:
            return " and ".join(text).capitalize()

    @staticmethod
    def get_selected_vertices(mesh_obj):
        vertices = []

        bm = bmesh.from_edit_mesh(mesh_obj.data)
        for i, v in enumerate(bm.verts):
            if v.select and not v.hide:
                vertices.append(i)

        return vertices

    @staticmethod
    def get_active_vertex(mesh_obj):
        bm = bmesh.from_edit_mesh(mesh_obj.data)
        av = bm.select_history.active

        if av:
            return av.index
        else:
            return -1

    def get_strategy_info(self, bone, mesh_obj):
        info, _ = Rig.get_bone_end_strategy(bone, self.is_tail)

        if "vertex_indices" in info:
            indices = info["vertex_indices"]

            if self.index < 0:
                selected = self.get_selected_vertices(mesh_obj)

                if not selected:
                    return None

                if info["strategy"] == "XYZ":
                    # Ensure 3 items
                    info["vertex_indices"] = [*selected, -1, -1, -1][0:3]
                else:
                    info["vertex_indices"] = selected
            elif 0 <= self.index <= len(indices):
                active = self.get_active_vertex(mesh_obj)

                if not active:
                    return None

                indices[self.index] = active
        elif "vertex_index" in info:
            active = self.get_active_vertex(mesh_obj)

            if not active:
                return None

            info["vertex_index"] = active
        else:
            return None

        return info

    def execute(self, context):
        bone = context.bone
        mesh = context.active_object

        if not (self.save or self.switch):
            return {'CANCELLED'}

        if self.save:
            info = self.get_strategy_info(bone, mesh)

            if not info:
                self.report({'ERROR'}, "Incorrect vertex selection")
                return {'CANCELLED'}

            bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

            for tgt_bone, tgt_tail in self.find_linked_bones(context, bone, self.is_tail,
                                                             use_strategy=True, use_location=True):
                Rig.assign_bone_end_strategy(tgt_bone, info, tgt_tail, force=True, lock=True)

            if rig_entity := self.get_rig_entity(bone):
                self.set_cursor_pos(context, rig_entity, info)

        if self.switch:
            self.switch_to_edit_bone(context, bone)
        else:
            bpy.ops.object.mode_set(mode="EDIT", toggle=False)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_Strategy_Vertices_Operator)
