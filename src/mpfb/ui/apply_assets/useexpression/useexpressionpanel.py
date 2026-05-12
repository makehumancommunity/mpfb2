"""File containing main UI for useexpression."""

import json, bpy

from .... import ClassManager
from ....services import LogService
from ....services import ObjectService
from ....services import UiService
from ....services.faceservice import FaceService, APPLIED_EXPRESSIONS_PROP
from ...abstractpanel import Abstract_Panel
from . import UseExpressionProperties

_LOG = LogService.get_logger("useexpression.useexpressionpanel")


class MPFB_PT_UseExpression_Panel(Abstract_Panel):
    """Apply saved expressions (and mix them) on a character."""

    bl_label = "Use expression"
    bl_category = UiService.get_value("CLOTHESCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Assets_Panel"

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        return ObjectService.find_object_of_type_amongst_nearest_relatives(
            context.active_object, "Basemesh"
        ) is not None

    def _draw_pack_hint(self, layout):
        box = self._create_box(layout, "Asset pack required", "ERROR")
        box.label(text="The faceunits01 asset pack is not installed.")
        box.label(text="Expressions cannot be applied until it is installed.")

    def _draw_picker(self, scene, layout):
        box = self._create_box(layout, "Apply expression", "TOOL_SETTINGS")
        UseExpressionProperties.draw_properties(scene, box, ["available_expression", "apply_weight"])
        box.operator("mpfb.apply_expression")

    def _draw_stack(self, scene, basemesh, layout):
        box = self._create_box(layout, "Currently applied", "TOOL_SETTINGS")
        try:
            raw = basemesh.get(APPLIED_EXPRESSIONS_PROP, "[]")
            stack = json.loads(raw) if isinstance(raw, str) else list(raw)
        except (ValueError, TypeError):
            stack = []

        if not stack:
            box.label(text="No expressions applied.")
            return

        for row in stack:
            if not isinstance(row, dict):
                continue
            asset = row.get("asset", "")
            weight = float(row.get("weight", 1.0))
            row_layout = box.row(align=True)
            row_layout.label(text=asset)
            # Weight is rendered as a label + edit-operator because Blender has no "slider that
            # calls an operator on change" widget.
            row_layout.label(text=f"{weight:.2f}")
            set_op = row_layout.operator("mpfb.set_expression_weight", text="", icon="GREASEPENCIL")
            set_op.asset = asset
            set_op.weight = weight
            rm_op = row_layout.operator("mpfb.remove_expression", text="", icon="X")
            rm_op.asset = asset

        box.operator("mpfb.clear_expression")

    def _draw_refit(self, scene, layout):
        box = self._create_box(layout, "Refit", "TOOL_SETTINGS")
        UseExpressionProperties.draw_properties(scene, box, ["auto_refit"])

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        if not FaceService.is_faceunits01_installed():
            self._draw_pack_hint(layout)
            return

        basemesh = self.get_basemesh(context, also_check_relatives=True)
        if basemesh is None:
            layout.label(text="No basemesh found.")
            return

        self._draw_refit(scene, layout)
        self._draw_picker(scene, layout)
        self._draw_stack(scene, basemesh, layout)


ClassManager.add_class(MPFB_PT_UseExpression_Panel)
