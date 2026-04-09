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

_LOG = LogService.get_logger("animops.repeatanim")

@pollstrategy(PollStrategy.ANY_ARMATURE_OBJECT_ACTIVE)
class MPFB_OT_Make_Cyclic_Operator(MpfbOperator):
    """Make animation cyclic by adding fcurve modifiers. WARNING: This will not work if the animation already has fcurve modifiers."""
    bl_idname = "mpfb.make_cyclic"
    bl_label = "Make cyclic"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        armature_object = context.active_object

        from ...animops.animopspanel import ANIMOPS_PROPERTIES  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=ANIMOPS_PROPERTIES)

        bone_name = None
        if ctx.shiftroot and ctx.rootbone:
            bone_name = ctx.rootbone

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        AnimationService.make_cyclic(armature_object, bone_name)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        self.report({'INFO'}, "Done")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Make_Cyclic_Operator)
