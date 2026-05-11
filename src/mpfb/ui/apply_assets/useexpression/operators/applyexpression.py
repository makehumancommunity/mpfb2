"""Operator that applies (or appends) an expression to the active basemesh."""

import os, bpy
from bpy.props import StringProperty, FloatProperty
from .....services import LogService
from .....services import ObjectService
from .....services import HumanService
from .....services.faceservice import FaceService
from ..... import ClassManager
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("useexpression.operators.applyexpression")


class MPFB_OT_Apply_Expression_Operator(MpfbOperator):
    """Apply the picked expression to the basemesh and append it to the stack."""

    bl_idname = "mpfb.apply_expression"
    bl_label = "Apply expression"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(name="filepath", description="Full path to expression JSON", default="")
    weight: FloatProperty(name="weight", description="Row weight", default=1.0, min=0.0, max=1.0)

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        if not FaceService.is_faceunits01_installed():
            self.report({'ERROR'}, "The faceunits01 asset pack is not installed")
            return {'CANCELLED'}

        active = context.active_object
        if active is None:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(active, "Basemesh")
        if basemesh is None:
            self.report({'ERROR'}, "No basemesh found")
            return {'CANCELLED'}

        # If filepath wasn't supplied (e.g. when the operator is called from the panel via a
        # button rather than the asset library), read from the picker enum.
        filepath = self.filepath
        if not filepath:
            from .. import UseExpressionProperties  # pylint: disable=C0415
            filepath = UseExpressionProperties.get_value("available_expression", entity_reference=context.scene)
            weight = float(UseExpressionProperties.get_value("apply_weight", entity_reference=context.scene))
        else:
            weight = float(self.weight)

        if not filepath:
            self.report({'ERROR'}, "No expression selected")
            return {'CANCELLED'}
        if not os.path.isfile(filepath):
            self.report({'ERROR'}, "Expression file does not exist: " + str(filepath))
            return {'CANCELLED'}

        try:
            FaceService.apply_expression_file(basemesh, filepath, weight=weight, append=True)
        except (IOError, ValueError) as exc:
            _LOG.error("Failed to apply expression", exc)
            self.report({'ERROR'}, f"Failed to apply expression: {exc}")
            return {'CANCELLED'}

        from .. import UseExpressionProperties  # pylint: disable=C0415
        if UseExpressionProperties.get_value("auto_refit", entity_reference=context.scene):
            HumanService.refit(active)

        self.report({'INFO'}, "Expression applied: " + os.path.basename(filepath))
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Apply_Expression_Operator)
