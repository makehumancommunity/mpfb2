"""Operator that edits the weight of a single row in the applied-expressions stack."""

import json
from bpy.props import StringProperty, FloatProperty
from .....services import LogService
from .....services import ObjectService
from .....services import HumanService
from .....services.faceservice import FaceService, APPLIED_EXPRESSIONS_PROP
from ..... import ClassManager
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("useexpression.operators.setexpressionweight")


class MPFB_OT_Set_Expression_Weight_Operator(MpfbOperator):
    """Change the weight of an already-applied expression and rebuild the stack."""

    bl_idname = "mpfb.set_expression_weight"
    bl_label = "Edit weight"
    bl_options = {'REGISTER', 'UNDO'}

    asset: StringProperty(name="asset", description="Library-relative asset path", default="")
    weight: FloatProperty(name="weight", description="New row weight", default=1.0, min=0.0, max=1.0)

    def get_logger(self):
        return _LOG

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def hardened_execute(self, context):
        if not self.asset:
            self.report({'ERROR'}, "No asset specified")
            return {'CANCELLED'}

        active = context.active_object
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(active, "Basemesh") if active else None
        if basemesh is None:
            self.report({'ERROR'}, "No basemesh found")
            return {'CANCELLED'}

        # Read, mutate, write back. Sorting + JSON-encoding happens in _write_applied_expressions.
        stack = FaceService._read_applied_expressions(basemesh)  # pylint: disable=W0212
        found = False
        new_stack = []
        for row in stack:
            if not isinstance(row, dict):
                continue
            if row.get("asset") == self.asset:
                new_stack.append({"asset": self.asset, "weight": float(self.weight)})
                found = True
            else:
                new_stack.append(row)
        if not found:
            self.report({'ERROR'}, "Asset is not currently applied: " + str(self.asset))
            return {'CANCELLED'}

        FaceService._write_applied_expressions(basemesh, new_stack)  # pylint: disable=W0212
        FaceService.rebuild_expression_stack(basemesh)

        from .. import UseExpressionProperties  # pylint: disable=C0415
        if UseExpressionProperties.get_value("auto_refit", entity_reference=context.scene):
            HumanService.refit(active)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Set_Expression_Weight_Operator)
