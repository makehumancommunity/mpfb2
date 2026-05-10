"""Operator that loads a saved expression JSON into the composer sliders."""

import os

from .....services import LogService
from .....services import ObjectService
from .....services.faceservice import FaceService, ARKIT_FACEUNITS
from ..... import ClassManager
from ....mpfboperator import MpfbOperator
from ....pollstrategy import pollstrategy, PollStrategy

_LOG = LogService.get_logger("makeexpression.operators.load")


@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_Compose_Expression_Load_Operator(MpfbOperator):
    """Load an expression JSON file into the composer sliders."""

    bl_idname = "mpfb.compose_expression_load"
    bl_label = "Load expression"
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

        scene = context.scene
        from .. import MakeExpressionProperties, write_slider_values  # pylint: disable=C0415

        active = context.active_object
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(active, "Basemesh") if active else None
        if basemesh is None:
            self.report({'ERROR'}, "Could not find a basemesh")
            return {'FINISHED'}

        selected = MakeExpressionProperties.get_value("available_expression", entity_reference=scene)
        if not selected:
            self.report({'ERROR'}, "No expression selected")
            return {'FINISHED'}

        if not os.path.isfile(selected):
            self.report({'ERROR'}, "Expression file does not exist: " + str(selected))
            return {'FINISHED'}

        expression_dict, metadata = FaceService.load_expression(selected)

        # Slider scene properties: zero everything first, then write loaded values. Suppress
        # per-slider update callbacks during the bulk write — we apply the dict to the basemesh
        # in a single set_expression call afterwards.
        zero_dict = {name: 0.0 for name in ARKIT_FACEUNITS}
        write_slider_values(scene, zero_dict)
        write_slider_values(scene, expression_dict)

        # Clear the basemesh first so a slider-by-slider apply doesn't accidentally accumulate
        # over a previous composition, then apply the loaded weights in bulk.
        FaceService.clear_expression(basemesh)
        if expression_dict:
            FaceService.set_expression(basemesh, expression_dict)

        # Restore metadata fields.
        MakeExpressionProperties.set_value("expression_name", metadata.get("name", ""), entity_reference=scene)
        MakeExpressionProperties.set_value("description", metadata.get("description", ""), entity_reference=scene)
        tags = metadata.get("tags", [])
        if isinstance(tags, list):
            tags = ", ".join(tags)
        MakeExpressionProperties.set_value("tags", str(tags), entity_reference=scene)
        MakeExpressionProperties.set_value("author", metadata.get("author", ""), entity_reference=scene)
        MakeExpressionProperties.set_value("copyright", metadata.get("copyright", ""), entity_reference=scene)
        MakeExpressionProperties.set_value("license", metadata.get("license", ""), entity_reference=scene)
        MakeExpressionProperties.set_value("homepage", metadata.get("homepage", ""), entity_reference=scene)

        self.report({'INFO'}, "Loaded expression: " + os.path.basename(selected))
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Compose_Expression_Load_Operator)
