"""Operator for recomputing bone head or tail offset from bone position strategy."""

import bpy
from mathutils import Vector

from mpfb.entities.rig import Rig
from mpfb.services.logservice import LogService
from mpfb import ClassManager

from .abstract import AbstractBoneOperator

_LOG = LogService.get_logger("boneops.set_bone_end_offset")


class MPFB_OT_Set_Bone_End_Offset_Operator(AbstractBoneOperator):
    """Set bone end offset from the difference between end position and strategy result"""
    bl_idname = "mpfb.set_bone_end_offset"
    bl_label = "Set Bone End Offset"
    bl_options = {'REGISTER', 'UNDO'}

    is_tail: bpy.props.BoolProperty(name="Tail")

    @classmethod
    def poll(cls, context):
        return cls.is_developer_bone_edit(context)

    def execute(self, context):
        bone = self.get_bone(context)

        # Check the strategy is valid
        info, _lock = Rig.get_bone_end_strategy(bone, self.is_tail)

        if not info:
            self.report({'ERROR'}, "Current strategy is not set.")
            return {'CANCELLED'}

        # Clear the offset before recalculating
        info["offset"] = (0, 0, 0)

        # Compute strategy result
        rig_entity = self.get_rig_entity(bone)

        if not rig_entity:
            return {'FINISHED'}

        calc_pos = rig_entity.get_best_location_from_strategy(info, use_default=False)

        if not calc_pos:
            self.report({'ERROR'}, "Cannot evaluate current strategy.")
            return {'FINISHED'}

        # Compute the new offset
        bone_pos = self.get_bone_position(bone, self.is_tail)

        offset = Vector(bone_pos) - Vector(calc_pos)

        if offset.magnitude > 1e-4:
            info["offset"] = tuple(offset)

        # Assign
        for tgt_bone, tgt_tail in self.find_linked_bones(context, bone, self.is_tail, use_strategy=True):
            Rig.assign_bone_end_strategy(tgt_bone, info, tgt_tail, force=True)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Set_Bone_End_Offset_Operator)
