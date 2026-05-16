"""Operator that saves the current slider composition as an expression JSON file."""

import os

from .....services import LogService
from .....services import LocationService
from .....services import ObjectService
from .....services.faceservice import FaceService, ARKIT_FACEUNITS
from ..... import ClassManager
from ....mpfboperator import MpfbOperator
from ....pollstrategy import pollstrategy, PollStrategy

_LOG = LogService.get_logger("makeexpression.operators.save")


@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_Compose_Expression_Save_Operator(MpfbOperator):
    """Save the current slider composition as a reusable expression asset."""

    bl_idname = "mpfb.compose_expression_save"
    bl_label = "Save expression to library"
    bl_options = {'REGISTER'}

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

        name = MakeExpressionProperties.get_value("expression_name", entity_reference=scene)
        name = str(name).strip() if name else ""

        if not name:
            self.report({'ERROR'}, "Must give a valid name")
            return {'FINISHED'}
        if "/" in name or "\\" in name:
            self.report({'ERROR'}, "Name must be given without path")
            return {'FINISHED'}
        if name == "." or name == "..":
            self.report({'ERROR'}, "Name is invalid, must include alphanumeric characters")
            return {'FINISHED'}

        expression_dict = {}
        for face_unit_name in ARKIT_FACEUNITS:
            value = MakeExpressionProperties.get_value(face_unit_name, entity_reference=scene)
            try:
                expression_dict[face_unit_name] = float(value) if value is not None else 0.0
            except (TypeError, ValueError):
                expression_dict[face_unit_name] = 0.0

        if not any(v != 0.0 for v in expression_dict.values()):
            self.report({'ERROR'}, "Expression has no non-zero face units")
            return {'FINISHED'}

        metadata = {
            "name": name,
            "description": str(MakeExpressionProperties.get_value("description", entity_reference=scene) or ""),
            "tags":        str(MakeExpressionProperties.get_value("tags", entity_reference=scene) or ""),
            "author":      str(MakeExpressionProperties.get_value("author", entity_reference=scene) or ""),
            "copyright":   str(MakeExpressionProperties.get_value("copyright", entity_reference=scene) or ""),
            "license":     str(MakeExpressionProperties.get_value("license", entity_reference=scene) or ""),
            "homepage":    str(MakeExpressionProperties.get_value("homepage", entity_reference=scene) or ""),
        }

        expressions_root = LocationService.get_user_data("expressions")
        if not os.path.exists(expressions_root):
            _LOG.debug("Will create", expressions_root)
            os.makedirs(str(expressions_root))

        absolute_file_path = os.path.abspath(os.path.join(expressions_root, name + ".json"))
        overwrite = bool(MakeExpressionProperties.get_value("overwrite", entity_reference=scene))
        if not overwrite and os.path.exists(absolute_file_path):
            self.report({'ERROR'}, "Expression file already exists: " + absolute_file_path)
            return {'FINISHED'}

        FaceService.save_expression(absolute_file_path, expression_dict, metadata)

        try:
            from .....ui.apply_assets.useexpression import refresh_expression_sliders  # pylint: disable=C0415
            refresh_expression_sliders()
        except Exception as exc:  # pylint: disable=W0703
            _LOG.warn("Could not refresh expression library sliders after save", exc)

        self.report({'INFO'}, "Expression written to " + absolute_file_path)
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Compose_Expression_Save_Operator)
