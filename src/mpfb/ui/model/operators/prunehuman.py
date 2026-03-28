"""Operator for pruning shapekeys."""

import bpy
from ....services import LogService
from ....services import TargetService
from ....services import ObjectService
from .... import ClassManager
from ...pollstrategy import pollstrategy, PollStrategy

_LOG = LogService.get_logger("model.prunehuman")

@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_PruneHumanOperator(bpy.types.Operator):
    """Remove all shape keys with a weight of < 0.0001"""
    bl_idname = "mpfb.prune_human"
    bl_label = "Prune shapekeys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Basemesh")
        ObjectService.activate_blender_object(basemesh, deselect_all=True)
        TargetService.prune_shapekeys(basemesh)

        self.report({'INFO'}, "Shape keys have tidied up")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_PruneHumanOperator)
