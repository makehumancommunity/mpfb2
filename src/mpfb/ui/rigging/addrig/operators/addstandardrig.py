"""Operator for adding a standard rig."""

from .....services import HumanService
from .....services import LogService
from .....services import ObjectService
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("addrig.add_standard_rig")

@pollstrategy(PollStrategy.BASEMESH_ACTIVE)
class MPFB_OT_AddStandardRigOperator(MpfbOperator):
    """Add a standard (non-rigify) rig"""

    bl_idname = "mpfb.add_standard_rig"
    bl_label = "Add standard rig"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        from ...addrig.addrigpanel import ADD_RIG_PROPERTIES  # pylint: disable=C0415
        from ....mpfbcontext import MpfbContext  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=ADD_RIG_PROPERTIES)

        if not ObjectService.object_is_basemesh(ctx.active_object):
            self.report({'ERROR'}, "Rigs can only be added to the base mesh")
            return {'FINISHED'}

        HumanService.add_builtin_rig(ctx.basemesh, ctx.standard_rig, import_weights=ctx.import_weights, operator=self)

        self.report({'INFO'}, "A rig was added")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_AddStandardRigOperator)
