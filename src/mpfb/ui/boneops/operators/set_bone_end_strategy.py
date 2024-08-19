"""Operator for recomputing bone head or tail position from strategy."""

import bpy

from mpfb.entities.rig import Rig, CLOSE_MEAN_SEARCH_RADIUS
from ....services import LogService
from mpfb import ClassManager

from .abstract import AbstractBoneOperator

_LOG = LogService.get_logger("boneops.set_bone_end_strategy")


class MPFB_OT_Set_Bone_End_Strategy_Operator(AbstractBoneOperator):
    """Set bone end strategy"""
    bl_idname = "mpfb.set_bone_end_strategy"
    bl_label = "Set Bone End Strategy"
    bl_options = {'REGISTER', 'UNDO'}

    is_tail: bpy.props.BoolProperty(name="Tail")
    strategy: bpy.props.StringProperty(name="Strategy")

    known_strategies = {
        "CUBE": (
            "Joint",
            "use the average position of vertices in a joint vertex group"
        ),
        "VERTEX": (
            "Vertex",
            "use the position of a single vertex"
        ),
        "MEAN": (
            "Mean",
            "use the average position of a list of vertices"
        ),
        "XYZ":  (
            "XYZ",
            "use the X,Y,Z location values taken from 3 separate vertices"
        ),
    }

    @classmethod
    def poll(cls, context):
        return cls.is_developer_bone_edit(context)

    @classmethod
    def description(cls, _context, props):
        info = cls.known_strategies.get(props.strategy)
        if info:
            return "Set bone end strategy: " + info[1] + ". Cursor is snapped to the position produced by the strategy"
        return None

    def compute_strategy(self, rig_entity, pos):
        info = {
            "strategy": self.strategy
        }

        if self.strategy == "CUBE":
            cube, dist = rig_entity.find_closest_cube(pos, max_allowed_dist=None)
            info["cube_name"] = cube or ""
        elif self.strategy == "VERTEX":
            index, dist = rig_entity.find_closest_vertex(pos, max_allowed_dist=None)
            info["vertex_index"] = index if index is not None else -1
        elif self.strategy == "MEAN":
            indices, dist = rig_entity.find_closest_vertex_mean(pos, search_radius=CLOSE_MEAN_SEARCH_RADIUS)
            if not indices:
                indices, dist = rig_entity.find_closest_vertex_mean(pos)
            if not indices:
                index, dist = rig_entity.find_closest_vertex(pos, max_allowed_dist=None)
                indices = [index if index is not None else -1]
            info["vertex_indices"] = indices
        elif self.strategy == "XYZ":
            index, dist = rig_entity.find_closest_vertex(pos, max_allowed_dist=None)
            if index is None:
                index = -1
            info["vertex_indices"] = [index, index, index]
        else:
            assert False

        return info

    def execute(self, context):
        assert self.strategy in self.known_strategies

        bone = self.get_bone(context)

        rig_entity = self.get_rig_entity(bone)

        if not rig_entity:
            return {'FINISHED'}

        bone_pos = self.get_bone_position(bone, self.is_tail)
        info = self.compute_strategy(rig_entity, bone_pos)

        for tgt_bone, tgt_tail in self.find_linked_bones(context, bone, self.is_tail,
                                                         use_strategy=True, use_location=True):
            Rig.assign_bone_end_strategy(tgt_bone, info, tgt_tail, force=True)

        self.set_cursor_pos(context, rig_entity, info)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Set_Bone_End_Strategy_Operator)
