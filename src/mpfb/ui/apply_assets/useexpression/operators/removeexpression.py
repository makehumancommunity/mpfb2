"""Operator that drops a row from the applied-expressions stack."""

from bpy.props import StringProperty
from .....services import LogService
from .....services import ObjectService
from .....services import HumanService
from .....services.faceservice import FaceService
from ..... import ClassManager
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("useexpression.operators.removeexpression")


class MPFB_OT_Remove_Expression_Operator(MpfbOperator):
    """Remove an expression from the applied stack."""

    bl_idname = "mpfb.remove_expression"
    bl_label = "Remove expression"
    bl_options = {'REGISTER', 'UNDO'}

    asset: StringProperty(name="asset", description="Library-relative asset path", default="")

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        if not self.asset:
            self.report({'ERROR'}, "No asset specified")
            return {'CANCELLED'}

        active = context.active_object
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(active, "Basemesh") if active else None
        if basemesh is None:
            self.report({'ERROR'}, "No basemesh found")
            return {'CANCELLED'}

        stack = FaceService._read_applied_expressions(basemesh)  # pylint: disable=W0212
        new_stack = [row for row in stack if isinstance(row, dict) and row.get("asset") != self.asset]
        FaceService._write_applied_expressions(basemesh, new_stack)  # pylint: disable=W0212
        FaceService.rebuild_expression_stack(basemesh)

        from .. import UseExpressionProperties  # pylint: disable=C0415
        if UseExpressionProperties.get_value("auto_refit", entity_reference=context.scene):
            HumanService.refit(active)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Remove_Expression_Operator)
