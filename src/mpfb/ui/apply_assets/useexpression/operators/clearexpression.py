"""Operator that empties the applied-expressions stack and zeroes face-unit shape keys."""

from .....services import LogService
from .....services import ObjectService
from .....services import HumanService
from .....services.faceservice import FaceService
from ..... import ClassManager
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("useexpression.operators.clearexpression")


class MPFB_OT_Clear_Expression_Operator(MpfbOperator):
    """Clear every applied expression and reset face-unit shape keys to neutral."""

    bl_idname = "mpfb.clear_expression"
    bl_label = "Clear all"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        active = context.active_object
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(active, "Basemesh") if active else None
        if basemesh is None:
            self.report({'ERROR'}, "No basemesh found")
            return {'CANCELLED'}

        FaceService.clear_applied_expressions(basemesh)

        from .. import UseExpressionProperties  # pylint: disable=C0415
        if UseExpressionProperties.get_value("auto_refit", entity_reference=context.scene):
            HumanService.refit(active)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Clear_Expression_Operator)
