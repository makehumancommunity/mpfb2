"""File containing main UI for makeexpression."""

import bpy

from .... import ClassManager
from ....services import LogService
from ....services import ObjectService
from ....services import UiService
from ....services.faceservice import FaceService, FACEUNIT_REGIONS
from ...abstractpanel import Abstract_Panel
from . import MakeExpressionProperties

_LOG = LogService.get_logger("makeexpression.makeexpressionpanel")

_REGION_LABELS = {
    "brow": "Brow",
    "eye": "Eye",
    "cheek": "Cheek",
    "jaw": "Jaw",
    "mouth": "Mouth",
    "nose": "Nose",
    "tongue": "Tongue",
}


class MPFB_PT_MakeExpression_Panel(Abstract_Panel):
    """MakeExpression — compose ARKit-style facial expressions."""

    bl_label = "MakeExpression"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Create_Panel"

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        return ObjectService.find_object_of_type_amongst_nearest_relatives(
            context.active_object, "Basemesh"
        ) is not None

    def _draw_refit(self, scene, layout):
        box = self._create_box(layout, "Refit", "TOOL_SETTINGS")
        MakeExpressionProperties.draw_properties(scene, box, ["auto_refit"])
        box.operator("mpfb.refit_human")

    def _draw_region(self, scene, layout, region_key, names):
        box = self._create_box(layout, _REGION_LABELS.get(region_key, region_key.title()), "TOOL_SETTINGS")
        MakeExpressionProperties.draw_properties(scene, box, list(names))

    def _draw_save(self, scene, layout):
        box = self._create_box(layout, "Save expression", "TOOL_SETTINGS")
        props = ["expression_name", "description", "tags", "author", "copyright",
                 "license", "homepage", "overwrite"]
        MakeExpressionProperties.draw_properties(scene, box, props)
        box.operator("mpfb.compose_expression_save")
        box.operator("mpfb.compose_expression_reset")

    def _draw_load(self, scene, layout):
        box = self._create_box(layout, "Load expression", "TOOL_SETTINGS")
        MakeExpressionProperties.draw_properties(scene, box, ["available_expression"])
        box.operator("mpfb.compose_expression_load")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        if not FaceService.is_faceunits01_installed():
            layout.label(text="Faceunits01 asset pack is not installed.")
            return

        self._draw_refit(scene, layout)

        for region_key, names in FACEUNIT_REGIONS.items():
            self._draw_region(scene, layout, region_key, names)

        self._draw_save(scene, layout)
        self._draw_load(scene, layout)


ClassManager.add_class(MPFB_PT_MakeExpression_Panel)
