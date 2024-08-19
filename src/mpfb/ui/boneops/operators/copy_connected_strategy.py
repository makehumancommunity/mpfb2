"""Operator for recomputing bone head or tail position from strategy."""

from mpfb.entities.rig import Rig
from ....services import LogService
from mpfb import ClassManager

from .abstract import AbstractBoneOperator

_LOG = LogService.get_logger("boneops.copy_connected_strategy")


class MPFB_OT_Copy_Connected_Strategy_Operator(AbstractBoneOperator):
    """Copy strategies from adjacent bones that touch ends with this one. Will not replace locked strategies, unless the other bone's strategy is also locked""" # noqa
    bl_idname = "mpfb.copy_connected_strategy"
    bl_label = "Copy Connected Strategies"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return cls.is_developer_bone_edit(context)

    def copy_end(self, context, bone, is_tail):
        info, lock = Rig.get_bone_end_strategy(bone, is_tail)

        best_info = None
        best_lock = False

        for tgt_bone, tgt_tail in self.find_linked_bones(context, bone, is_tail, use_self=False, force=True,
                                                         use_strategy=False, use_location=True):
            info2, lock2 = Rig.get_bone_end_strategy(tgt_bone, tgt_tail)

            if info2 and info2 != info:
                if not best_info or lock2 and not best_lock:
                    best_info = info2
                    best_lock = lock2

        if best_info and (best_lock or not lock):
            Rig.assign_bone_end_strategy(bone, best_info, is_tail, force=True, lock=best_lock)
            return True

    def execute(self, context):
        bone = self.get_bone(context)

        names = []

        if self.copy_end(context, bone, False):
            names.append("head")

        if self.copy_end(context, bone, True):
            names.append("tail")

        if names:
            self.report({'INFO'}, f"Updated {' and '.join(names)} strategy.")
        else:
            self.report({'WARNING'}, "No suitable matches found.")

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Copy_Connected_Strategy_Operator)
