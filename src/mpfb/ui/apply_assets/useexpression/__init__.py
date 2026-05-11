"""Use-expression panel — apply saved ARKit expressions to a character.

Lives under the ``Apply assets`` parent panel. Provides a persistent-stack model: one or more
saved ``.json`` expressions can be applied with per-row weights, edited live, removed, or
cleared. The stack lives in ``basemesh["mpfb_applied_expressions"]`` and round-trips through
the human preset (see ``HumanService.serialize_to_json_string``).

This module is parallel in structure to ``ui/apply_assets/assetlibrary/`` and intentionally
*not* a sibling of the composer (the composer lives under ``ui/create_assets/``).
"""

import os, bpy

from ....services import LogService
from ....services import SceneConfigSet
from ....services.faceservice import FaceService

_LOG = LogService.get_logger("useexpression.init")
_LOG.trace("initializing useexpression module")


def _populate_picker_items(self, context):
    """Items callback for the use-panel's expression picker enum.

    Shares the scan with the composer via ``FaceService.list_available_expressions``. The
    visible label is the library-relative path without ``.json``; metadata's ``description``
    becomes the tooltip when available.
    """
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
