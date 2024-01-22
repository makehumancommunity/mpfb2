"""Operator for a human with feet on ground."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.humanservice import HumanService
from mpfb.services.objectservice import ObjectService
from mpfb import ClassManager

_LOG = LogService.get_logger("model.feet_on_ground")

class MPFB_OT_TranslateHumanOperator(bpy.types.Operator):
    """ Translate the basemesh for feet to touch the ground. This is needed if you have changed modeling sliders for leg length"""
    bl_idname = "mpfb.feet_on_ground"
    bl_label = "Make feet touch the ground"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Basemesh")
        ObjectService.activate_blender_object(basemesh, deselect_all=True)
        HumanService.feet_on_ground(basemesh)

        self.report({'INFO'}, "Assets have been translated")
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Basemesh")
        return basemesh is not None

ClassManager.add_class(MPFB_OT_TranslateHumanOperator)
