"""This module provides the composer panel for ARKit-based facial expressions."""

import os, bpy

from ....services import LogService
from ....services import ObjectService
from ....services import SceneConfigSet
from ....services.faceservice import (
    FaceService,
    ARKIT_FACEUNITS,
    FACEUNIT_DESCRIPTIONS,
)

_LOG = LogService.get_logger("makeexpression.init")
_LOG.trace("initializing makeexpression module")

_ROOT = os.path.dirname(__file__)
_PROPERTIES_DIR = os.path.join(_ROOT, "properties")

# Flipped by bulk slider writes to make the per-slider update callbacks no-op.
_SUPPRESS_UPDATE = False


def _is_update_suppressed():
    return _SUPPRESS_UPDATE


def _set_update_suppressed(value):
    global _SUPPRESS_UPDATE
    _SUPPRESS_UPDATE = bool(value)


def _make_slider_update(face_unit_name):
    """Build an update callback for a single ARKit face unit slider."""

    def _update(self, context):
        if _is_update_suppressed():
            return
        active = context.active_object
        if active is None:
            return
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(active, "Basemesh")
        if basemesh is None:
            return
        weight = getattr(self, "MPFB_EX_" + face_unit_name, 0.0)
        try:
            FaceService.set_expression(basemesh, {face_unit_name: float(weight)})
            if MakeExpressionProperties.get_value("auto_refit", entity_reference=context.scene):
                from ....services import HumanService  # pylint: disable=C0415
                HumanService.refit(active)
        except Exception as e:  # pylint: disable=W0703
            _LOG.error("Failed to apply slider value live", (face_unit_name, weight, e))

    return _update


# `available_expression` needs an items_callback, so it is registered separately below.
_definitions = [
    d for d in SceneConfigSet.get_definitions_in_json_directory(_PROPERTIES_DIR)
    if d.get("name") != "available_expression"
]
MakeExpressionProperties = SceneConfigSet(_definitions, prefix="EX_")  # pylint: disable=C0103


def _populate_available_expressions(self, context):
    """Items callback for the load_expression enum."""
    _LOG.enter()

    enum_items = []
    for idx, (abs_path, rel_path, _metadata) in enumerate(FaceService.list_available_expressions()):
        label = os.path.splitext(rel_path)[0]
        enum_items.append((abs_path, label, label, idx))
    return enum_items


_AVAILABLE_EXPRESSION_DEF = next(
    d for d in SceneConfigSet.get_definitions_in_json_directory(_PROPERTIES_DIR)
    if d.get("name") == "available_expression"
)
MakeExpressionProperties.add_property(
    _AVAILABLE_EXPRESSION_DEF,
    items_callback=_populate_available_expressions,
)

# 52 face-unit sliders are registered procedurally rather than as one JSON file each.
for _name in ARKIT_FACEUNITS:
    _slider_def = {
        "type": "float",
        "name": _name,
        "label": _name,
        "description": FACEUNIT_DESCRIPTIONS.get(_name, _name),
        "default": 0.0,
        "min": 0.0,
        "max": 1.0,
    }
    MakeExpressionProperties.add_property(
        _slider_def,
        update_callback=_make_slider_update(_name),
    )


def reset_slider_values(scene):
    """Reset every face unit slider on the given scene to 0.0 without triggering update callbacks."""
    _set_update_suppressed(True)
    try:
        for face_unit_name in ARKIT_FACEUNITS:
            full_name = "MPFB_EX_" + face_unit_name
            if hasattr(scene, full_name):
                setattr(scene, full_name, 0.0)
    finally:
        _set_update_suppressed(False)


def write_slider_values(scene, expression_dict):
    """Write a {face_unit_name: weight} dict into the slider scene properties without firing update callbacks."""
    _set_update_suppressed(True)
    try:
        for face_unit_name in ARKIT_FACEUNITS:
            full_name = "MPFB_EX_" + face_unit_name
            value = float(expression_dict.get(face_unit_name, 0.0))
            if hasattr(scene, full_name):
                setattr(scene, full_name, value)
    finally:
        _set_update_suppressed(False)


from .makeexpressionpanel import MPFB_PT_MakeExpression_Panel
from .operators import *  # noqa: F401,F403

__all__ = [
    "MPFB_PT_MakeExpression_Panel",
    "MakeExpressionProperties",
    "reset_slider_values",
    "write_slider_values",
]
