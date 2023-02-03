from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.materialservice import MaterialService
from mpfb.services.objectservice import ObjectService
from mpfb.services.rigservice import RigService
from mpfb.services.animationservice import AnimationService
from mpfb._classmanager import ClassManager
import bpy, json, math, os
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper

_LOG = LogService.get_logger("makepose.operators.retarget")

class MPFB_OT_Retarget_Operator(bpy.types.Operator):
    """Retarget animation"""
    bl_idname = "mpfb.retarget"
    bl_label = "Retarget"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        # TODO: check current mode
        return True

    def execute(self, context):
        _LOG.enter()

        if context.object is None or context.object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        target = None
        source = None

        for obj in bpy.context.selected_objects:
            if obj.type == 'ARMATURE':
                if RigService.identify_rig(obj) != "unknown":
                    target = obj
                else:
                    source = obj

        if not target or not source:
            self.report({'ERROR'}, "Not enough armatures selected")
            return {'FINISHED'}

        AnimationService.retarget(source, target)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Retarget_Operator)
