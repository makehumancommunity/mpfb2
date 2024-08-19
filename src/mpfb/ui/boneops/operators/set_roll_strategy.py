"""Operator for recomputing bone head or tail position from strategy."""

import bpy

from mpfb.entities.rig import Rig
from ....services import LogService
from .... import ClassManager

from .. import BoneOpsEditBoneProperties
from .abstract import AbstractBoneOperator

_LOG = LogService.get_logger("boneops.set_roll_strategy")


class MPFB_OT_Set_Roll_Strategy_Operator(AbstractBoneOperator):
    """Set roll strategy"""
    bl_idname = "mpfb.set_roll_strategy"
    bl_label = "Set Roll Strategy"
    bl_options = {'REGISTER', 'UNDO'}

    strategy: bpy.props.StringProperty(name="Strategy")

    known_strategies = {
        "": (
            "Use Current Roll",
            "use the current roll value of the bone as is"
        ),
        "ALIGN_X_WORLD_X": (
            "Align X to World X",
            "align bone X to world X"
        ),
        "ALIGN_Z_WORLD_Z": (
            "Align Z to World Z",
            "align bone Z to world Z"
        ),
    }

    @classmethod
    def poll(cls, context):
        return cls.is_developer_bone_edit(context)

    @classmethod
    def description(cls, _context, props):
        info = cls.known_strategies.get(props.strategy)
        if info:
            return "Set roll strategy: " + info[1]
        return None

    def execute(self, context):
        assert self.strategy in self.known_strategies

        bone = context.edit_bone

        BoneOpsEditBoneProperties.set_value("roll_strategy", self.strategy, entity_reference=bone)

        Rig.apply_bone_roll_strategy(bone, self.strategy)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Set_Roll_Strategy_Operator)
