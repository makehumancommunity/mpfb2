"""Operator for adding a rigify meta rig."""

from .....services import HumanService
from .....services import LogService
from .....services import ObjectService
from .....services import RigService
from .....services import SystemService
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext

_LOG = LogService.get_logger("rigifyrig.add_rigify_rig")

@pollstrategy(PollStrategy.BASEMESH_ACTIVE)
class MPFB_OT_AddRigifyRigOperator(MpfbOperator):
    """Add a rigify rig"""

    bl_idname = "mpfb.add_rigify_rig"
    bl_label = "Add rigify rig"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        if not SystemService.check_for_rigify():
            self.report({'ERROR'}, "The rigify addon isn't enabled. You need to enable it under preferences.")
            return {'FINISHED'}

        from ...rigifyrig.rigifyrigpanel import RIGIFY_RIG_PROPERTIES  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=RIGIFY_RIG_PROPERTIES)

        if not ObjectService.object_is_basemesh(ctx.active_object):
            self.report({'ERROR'}, "Rigs can only be added to the base mesh")
            return {'FINISHED'}

        meta_rig = HumanService.add_builtin_rig(ctx.basemesh, "rigify." + ctx.rigify_rig, import_weights=ctx.import_weights_rigify, operator=self)

        if not ctx.auto_generate:
            self.report({'INFO'}, "A rig was added")
            return {'FINISHED'}

        if meta_rig is None:
            meta_rig = ObjectService.find_object_of_type_amongst_nearest_relatives(ctx.basemesh, "Skeleton")

        if meta_rig is None:
            self.report({'WARNING'}, "Rig was added but the meta rig could not be located for auto-generation.")
            return {'FINISHED'}

        rigify_object = RigService.generate_rigify_rig(
            meta_rig,
            name=ctx.name,
            meta_rig_action=ctx.meta_rig_action,
        )

        if rigify_object is None:
            self.report({'WARNING'}, "Meta rig was added but Rigify considers it invalid; the full rig was not generated.")
            return {'FINISHED'}

        self.report({'INFO'}, "A rig was added and generated")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_AddRigifyRigOperator)
