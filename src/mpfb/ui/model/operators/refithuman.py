"""Operator for refitting a human."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.humanservice import HumanService
from mpfb.services.objectservice import ObjectService
from mpfb import ClassManager

_LOG = LogService.get_logger("model.refithuman")

class MPFB_OT_RefitHumanOperator(bpy.types.Operator):
    """Refit clothes, bodyparts, proxy and rig to the basemesh. This is needed if you have changed modeling sliders after having added such assets."""
    bl_idname = "mpfb.refit_human"
    bl_label = "Refit assets to basemesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        blender_object = context.active_object
        HumanService.refit(blender_object)

        self.report({'INFO'}, "Assets have been refitted")
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj:
            return False

        if ObjectService.object_is_basemesh_or_body_proxy(obj):
            return True

        if ObjectService.object_is_skeleton(obj):
            return True

        return False

ClassManager.add_class(MPFB_OT_RefitHumanOperator)

