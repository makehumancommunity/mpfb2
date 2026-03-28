"""Operator for refitting a human."""

import bpy
from ....services import LogService
from ....services import HumanService
from ....services import ObjectService
from .... import ClassManager
from ...pollstrategy import pollstrategy, PollStrategy

_LOG = LogService.get_logger("model.refithuman")

@pollstrategy(PollStrategy.BASEMESH_OR_BODY_PROXY_OR_SKELETON_ACTIVE)
class MPFB_OT_RefitHumanOperator(bpy.types.Operator):
    """Refit clothes, bodyparts, proxy and rig to the basemesh. This is needed if you have changed modeling sliders after having added such assets"""
    bl_idname = "mpfb.refit_human"
    bl_label = "Refit assets to basemesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        blender_object = context.active_object
        HumanService.refit(blender_object)

        self.report({'INFO'}, "Assets have been refitted")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_RefitHumanOperator)

