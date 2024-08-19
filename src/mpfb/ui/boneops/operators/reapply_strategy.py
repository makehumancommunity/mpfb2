"""Operator for recomputing bone head or tail position from strategy."""

import bpy
from ....services import LogService
from mpfb import ClassManager

from .abstract import AbstractBoneOperator

_LOG = LogService.get_logger("boneops.reapply_strategy")


class MPFB_OT_Reapply_Bone_Strategy_Operator(AbstractBoneOperator):
    """Recompute bone end position from strategy"""
    bl_idname = "mpfb.reapply_strategy"
    bl_label = "Reapply Strategy"
    bl_options = {'REGISTER', 'UNDO'}

    is_tail: bpy.props.BoolProperty(name="Tail")

    @classmethod
    def poll(cls, context):
        return cls.is_developer_bone_edit(context)

    def execute(self, context):
        bone = self.get_bone(context)

        rig_entity = self.get_rig_entity(context.active_object)

        if not rig_entity:
            return {'FINISHED'}

        _, pos = rig_entity.get_bone_strategy_and_location(bone, self.is_tail)

        if not pos:
            self.report({'ERROR'}, "Could not compute a new position.")
            return {'FINISHED'}

        for tgt_bone, tgt_tail in self.find_linked_bones(context, bone, self.is_tail, use_strategy=True):
            if tgt_tail:
                tgt_bone.tail = pos
            else:
                tgt_bone.head = pos

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Reapply_Bone_Strategy_Operator)
