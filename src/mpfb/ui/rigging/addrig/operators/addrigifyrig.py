"""Operator for adding a rigify rig."""

from .....services import HumanService
from .....services import LogService
from .....services import ObjectService
from .....services import SystemService
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext

_LOG = LogService.get_logger("addrig.add_rigify_rig")

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

        from ...addrig.addrigpanel import ADD_RIG_PROPERTIES  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=ADD_RIG_PROPERTIES)

        if not ObjectService.object_is_basemesh(ctx.active_object):
            self.report({'ERROR'}, "Rigs can only be added to the base mesh")
            return {'FINISHED'}

        HumanService.add_builtin_rig(ctx.basemesh, "rigify." + ctx.rigify_rig, import_weights=ctx.import_weights_rigify, operator=self)

        self.report({'INFO'}, "A rig was added")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_AddRigifyRigOperator)
