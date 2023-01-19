"""Operator for pruning shapekeys."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.targetservice import TargetService
from mpfb.services.objectservice import ObjectService
from mpfb import ClassManager

_LOG = LogService.get_logger("model.prunehuman")

class MPFB_OT_PruneHumanOperator(bpy.types.Operator):
    """Remove all shape keys with a weight of < 0.0001"""
    bl_idname = "mpfb.prune_human"
    bl_label = "Prune shapekeys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Basemesh")
        ObjectService.activate_blender_object(basemesh, deselect_all=True)
        TargetService.prune_shapekeys(basemesh)

        self.report({'INFO'}, "Shape keys have been removed")
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Basemesh")
        return basemesh is not None

ClassManager.add_class(MPFB_OT_PruneHumanOperator)

