"""Operator for generating a final rigify rig from a meta-rig."""

from .....services import LogService
from .....services import ObjectService
from .....services import RigService
from .....services import SystemService
from ..... import ClassManager
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext

_LOG = LogService.get_logger("rigifyrig.generate_rigify_rig")

class MPFB_OT_GenerateRigifyRigOperator(MpfbOperator):
    """Generate a rigify rig from a meta-rig"""

    bl_idname = "mpfb.generate_rigify_rig"
    bl_label = "Generate"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            if not ObjectService.object_is_any_skeleton(context.active_object):
                return False
            rig_type = RigService.identify_rig(context.active_object)
            return rig_type.startswith("rigify.")
        return False

    def hardened_execute(self, context):
        from ...rigifyrig.rigifyrigpanel import RIGIFY_RIG_PROPERTIES  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=RIGIFY_RIG_PROPERTIES)

        if not ObjectService.object_is_any_skeleton(ctx.active_object):
            self.report({'ERROR'}, "Must have armature object selected")
            return {'FINISHED'}

        if not SystemService.check_for_rigify():
            self.report({'ERROR'}, "The rigify addon isn't enabled. You need to enable it under preferences.")
            return {'FINISHED'}

        rigify_object = RigService.generate_rigify_rig(
            ctx.active_object,
            name=ctx.name,
            meta_rig_action=ctx.meta_rig_action,
        )

        if rigify_object is None:
            self.report({'WARNING'}, "Rigify considers the meta rig invalid. Check that the rigify configuration on the bones is intact.")
            return {'FINISHED'}

        self.report({'INFO'}, "A rig was generated")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_GenerateRigifyRigOperator)
