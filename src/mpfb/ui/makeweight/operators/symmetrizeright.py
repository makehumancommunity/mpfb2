"""Operator for making right side a mirrored copy of left side."""

import bpy
from ....services import LogService
from ....services import ObjectService
from ....services import RigService
from mpfb import ClassManager

_LOG = LogService.get_logger("makeweight.symmetrizeright")

class MPFB_OT_SymmetrizeRightOperator(bpy.types.Operator):
    """Symmetrize by finding all left-side bone groups and copying their weights to the corresponding right-side bone groups"""
    bl_idname = "mpfb.symmetrize_makeweight_right"
    bl_label = "Copy left to right"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        if ObjectService.object_is_basemesh(context.active_object):
            return True
        if ObjectService.object_is_skeleton(context.active_object):
            return True
        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Skeleton")
        if rig:
            return True
        return False

    def execute(self, context):

        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Skeleton")
        if not rig:
            self.report({'ERROR'}, "Could not find a rig amongst nearest relatives")
            return {'FINISHED'}

        RigService.symmetrize_all_bone_weights(rig, True)

        self.report({'INFO'}, "Weight symmetrized")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_SymmetrizeRightOperator)
