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

_LOG = LogService.get_logger("makepose.operators.loadanimation")

@pollstrategy(PollStrategy.ANY_ARMATURE_OBJECT_ACTIVE)
class MPFB_OT_Load_Animation_Operator(MpfbOperator):
    """Load animation from json"""
    bl_idname = "mpfb.load_animation"
    bl_label = "Load animation"
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

        with open('/tmp/animation.json', 'r') as json_file:
            animation = json.load(json_file)
        _LOG.dump("Animation", animation)

        AnimationService.set_key_frames_from_dict(armature_object, animation, ik_bone_translation=ctx.iktrans, root_bone_translation=ctx.roottrans, fk_bone_translation=ctx.fktrans)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        self.report({'INFO'}, "Done")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Animation_Operator)
