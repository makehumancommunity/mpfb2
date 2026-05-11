"""Operator that loads a saved expression JSON into the composer sliders."""

import os

from .....services import LogService
from .....services import ObjectService
from .....services.faceservice import FaceService
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
        from .. import MakeExpressionProperties  # pylint: disable=C0415

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

        # Re-read metadata for the composer's metadata fields. apply_expression_file does its
        # own load_expression internally for the face-unit values; this second call is cheap and
        # keeps the helper's return contract simple.
        _expr, metadata = FaceService.load_expression(selected)

        # A composer load is a "replace what I'm composing with this file" action, so the stack
        # is replaced with a single row (append=False). The helper handles clear + set + the
        # composer slider mirror in one pass.
        try:
            FaceService.apply_expression_file(basemesh, selected, weight=1.0, append=False)
        except (IOError, ValueError) as exc:
            _LOG.error("Failed to load expression", exc)
            self.report({'ERROR'}, f"Failed to load expression: {exc}")
            return {'CANCELLED'}

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
