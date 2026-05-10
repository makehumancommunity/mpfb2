"""Operator that clears all face unit shape keys and resets all sliders to 0.0."""

from .....services import LogService
from .....services import ObjectService
from .....services.faceservice import FaceService
from ..... import ClassManager
from ....mpfboperator import MpfbOperator
from ....pollstrategy import pollstrategy, PollStrategy

_LOG = LogService.get_logger("makeexpression.operators.reset")


@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_Compose_Expression_Reset_Operator(MpfbOperator):
    """Reset all face unit sliders and shape keys to neutral (0.0)."""

    bl_idname = "mpfb.compose_expression_reset"
    bl_label = "Reset all"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    @classmethod
    def poll(cls, context):
        if not FaceService.is_faceunits01_installed():
            return False
        if context.active_object is None:
            return False
        return ObjectService.find_object_of_type_amongst_nearest_relatives(
            context.active_object, "Basemesh"
        ) is not None

    def hardened_execute(self, context):
        _LOG.enter()

        active = context.active_object
        if active is None:
            self.report({'ERROR'}, "Could not find a basemesh")
            return {'FINISHED'}

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(active, "Basemesh")
        if basemesh is None:
            self.report({'ERROR'}, "Could not find a basemesh")
            return {'FINISHED'}

        from .. import reset_slider_values  # pylint: disable=C0415

        FaceService.clear_expression(basemesh)
        reset_slider_values(context.scene)

        self.report({'INFO'}, "All face unit sliders reset to 0.0")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Compose_Expression_Reset_Operator)
