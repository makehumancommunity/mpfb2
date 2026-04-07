from .....services import LogService
from .....services import LocationService
from .....services import MaterialService
from .....services import ObjectService
from .....services import AnimationService
from .....services import RigService
from ..... import ClassManager
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext
from ....pollstrategy import pollstrategy, PollStrategy
import bpy, json, math, os
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper

_LOG = LogService.get_logger("makepose.operators.saveanimation")

@pollstrategy(PollStrategy.ANY_ARMATURE_OBJECT_ACTIVE)
class MPFB_OT_Save_Animation_Operator(MpfbOperator):
    """Save animation as json"""
    bl_idname = "mpfb.save_animation"
    bl_label = "Save animation"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        if context.active_object is None or context.active_object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        armature_object = context.active_object

        from ...makepose import MakePoseProperties
        ctx = MpfbContext(context=context, scene_properties=MakePoseProperties)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        animation = AnimationService.get_key_frames_as_dict(armature_object, ik_bone_translation=ctx.iktrans, root_bone_translation=ctx.roottrans, fk_bone_translation=ctx.fktrans)
        _LOG.dump("Animation", animation)

        with open('/tmp/animation.json', 'w') as json_file:
            json.dump(animation, json_file, indent=4, sort_keys=True)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        self.report({'INFO'}, "Done")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Save_Animation_Operator)
