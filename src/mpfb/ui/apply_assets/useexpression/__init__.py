"""This module provides the use-expression panel for applying saved ARKit expressions."""

import os, bpy

from ....services import LogService
from ....services import SceneConfigSet
from ....services.faceservice import FaceService

_LOG = LogService.get_logger("useexpression.init")
_LOG.trace("initializing useexpression module")


def _populate_picker_items(self, context):
    """Items callback for the use-panel's expression picker enum."""
    _LOG.enter()
    items = []
    for idx, (abs_path, rel_path, metadata) in enumerate(FaceService.list_available_expressions()):
        label = os.path.splitext(rel_path)[0]
        description = metadata.get("description", "") if isinstance(metadata, dict) else ""
        items.append((abs_path, label, description or label, idx))
    return items


UseExpressionProperties = SceneConfigSet([
    {
        "type": "boolean",
        "name": "auto_refit",
        "description": "Automatically refit the human after each expression change",
        "label": "Auto refit",
        "default": True,
    },
    {
        "type": "float",
        "name": "apply_weight",
        "description": "Row weight to use when applying the picked expression",
        "label": "Weight",
        "default": 1.0,
        "min": 0.0,
        "max": 1.0,
    },
], prefix="USEEXPR_")


UseExpressionProperties.add_property(
    {
        "type": "enum",
        "name": "available_expression",
        "description": "Pick an expression to apply",
        "label": "Expression",
        "default": None,
    },
    items_callback=_populate_picker_items,
)


from .useexpressionpanel import MPFB_PT_UseExpression_Panel  # noqa: E402
from .operators import *  # noqa: F401,F403,E402

__all__ = [
    "MPFB_PT_UseExpression_Panel",
    "UseExpressionProperties",
]
