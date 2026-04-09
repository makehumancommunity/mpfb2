"""Operator for adding a custom rig from the user library."""

from .....services import HumanService
from .....services import LogService
from .....services import ObjectService
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext

_LOG = LogService.get_logger("addrig.add_custom_rig")

@pollstrategy(PollStrategy.BASEMESH_ACTIVE)
class MPFB_OT_Add_Custom_Rig_Operator(MpfbOperator):
    """Add a custom rig from the user library to the active basemesh"""

    bl_idname = "mpfb.add_custom_rig"
    bl_label = "Add custom rig"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        from ...addrig.addrigpanel import ADD_RIG_PROPERTIES  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=ADD_RIG_PROPERTIES)

        if not ObjectService.object_is_basemesh(ctx.active_object):
            self.report({'ERROR'}, "Custom rigs can only be added to the base mesh")
            return {'FINISHED'}

        if not ctx.custom_rig or ctx.custom_rig == "NONE":
            self.report({'ERROR'}, "No custom rig selected")
            return {'FINISHED'}

        HumanService.add_custom_rig(ctx.basemesh, "custom." + ctx.custom_rig, import_weights=ctx.import_weights_custom, operator=self)

        self.report({'INFO'}, "Custom rig '" + ctx.custom_rig + "' was added")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Add_Custom_Rig_Operator)
