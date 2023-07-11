from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.materialservice import MaterialService
from mpfb.services.objectservice import ObjectService
from mpfb.services.animationservice import AnimationService
from mpfb.services.rigservice import RigService
from mpfb._classmanager import ClassManager
from mpfb.ui.mpfboperator import MpfbOperator
import bpy, json, math, os
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper

_LOG = LogService.get_logger("animops.repeatanim")

class MPFB_OT_Repeat_Animation_Operator(MpfbOperator):
    """WARNING: THIS IS RATHER EXPERIMENTAL. Repeat an animation by copying its keyframes, optionally with given offsets and distance shifts. Note that if all you want is to make an animation cyclic, this is probably overkill"""
    bl_idname = "mpfb.repeat_animation"
    bl_label = "Repeat animation"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        MpfbOperator.__init__(self, "animops.repeatanim")

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        return True

    def hardened_execute(self, context):
        _LOG.enter()

        if context.object is None or context.object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'CANCELLED'}

        armature_object = context.object

        from mpfb.ui.animops.animopspanel import ANIMOPS_PROPERTIES

        iterations = ANIMOPS_PROPERTIES.get_value('iterations', entity_reference=context.scene)
        offset = ANIMOPS_PROPERTIES.get_value('offset', entity_reference=context.scene)
        skipfirst = ANIMOPS_PROPERTIES.get_value('skipfirst', entity_reference=context.scene)

        skip = 0
        if skipfirst:
            skip = 1

        if not iterations:
            self.report({'ERROR'}, "Must specify a positive number of iterations")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        max_keyframe = AnimationService.get_max_keyframe(armature_object)
        _LOG.debug("max_keyframe", max_keyframe)

        total_distance = AnimationService.get_bone_movement_distance(armature_object, "mixamorig:Hips", skip, max_keyframe)
        first_distance = AnimationService.get_bone_movement_distance(armature_object, "mixamorig:Hips", skip, skip+1)
        _LOG.debug("total_distance", total_distance)
        _LOG.debug("first_distance", first_distance)
        distance = total_distance

        for i in range(iterations):
            first_keyframe = max_keyframe + offset + (i*(max_keyframe-skip))
            last_keyframe = first_keyframe + max_keyframe - skip
            _LOG.debug("first, last, skip", (first_keyframe, last_keyframe, skip))
            AnimationService.duplicate_keyframes(armature_object, first_keyframe, skip, max_keyframe)

            currdist = [distance[0] * (i+1), distance[1] * (i+1), distance[2] * (i+1)]
            AnimationService.move_bone_for_all_keyframes(armature_object, "mixamorig:Hips", currdist, first_keyframe, last_keyframe)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        self.report({'INFO'}, "Done")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Repeat_Animation_Operator)
