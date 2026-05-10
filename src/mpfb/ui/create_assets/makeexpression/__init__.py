"""Composer for ARKit-based facial expressions.

Adds the ``MakeExpression`` panel under the ``Create assets`` parent panel. The panel exposes one
slider per ARKit face unit (52 in total, grouped by region) plus metadata fields, and three
operators (reset, save, load) that produce/consume the JSON format documented in
``docs/fileformats/expression.md``.

Slider properties are not defined as JSON files (they would be 52 near-identical files); they are
built dynamically from ``ARKIT_FACEUNITS`` and registered with per-unit Blender ``update``
callbacks so that dragging a slider drives the corresponding ``!ex-<name>`` shape key live.
"""

import os, bpy

from ....services import LogService
from ....services import LocationService
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

# Module-level guard. The load operator flips this to True around its bulk slider assignment so the
# 52 per-slider update callbacks no-op; the operator then calls FaceService.set_expression once on
# the basemesh. Blender drives property-change callbacks on the main thread, so a plain global
# flag is sufficient — concurrent slider drags are not possible.
_SUPPRESS_UPDATE = False


def _is_update_suppressed():
    return _SUPPRESS_UPDATE


def _set_update_suppressed(value):
    global _SUPPRESS_UPDATE
    _SUPPRESS_UPDATE = bool(value)


def _make_slider_update(face_unit_name):
    """Build an update callback for a single ARKit face unit slider.

    The callback runs whenever the user drags the slider in the UI. It locates the basemesh among
    the active object's nearest relatives and routes the new weight through
    ``FaceService.set_expression`` — which handles on-demand shape key load if the corresponding
    ``!ex-<name>`` shape key has not yet been created on the basemesh.
    """

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


# Register all simple metadata properties + the overwrite toggle in one call.
# `available_expression` needs an items_callback, so it is excluded here and
# registered explicitly below.
_definitions = [
    d for d in SceneConfigSet.get_definitions_in_json_directory(_PROPERTIES_DIR)
    if d.get("name") != "available_expression"
]
MakeExpressionProperties = SceneConfigSet(_definitions, prefix="EX_")  # pylint: disable=C0103


def _populate_available_expressions(self, context):
    """Items callback for the load_expression enum.

    Scans two roots in priority order — user expressions under
    ``<user_data>/expressions/`` and system-shipped expressions under
    ``<mpfb_data>/expressions/``. Files are deduplicated by basename with the user copy winning
    when names collide, matching the convention used for poses.
    """
    _LOG.enter()

    def _scan(directory):
        items = []
        if not directory or not os.path.isdir(directory):
            return items
        for name in os.listdir(directory):
            if not name.lower().endswith(".json"):
                continue
            items.append((os.path.splitext(name)[0], os.path.join(directory, name)))
        return items

    user_dir = LocationService.get_user_data("expressions")
    system_dir = LocationService.get_mpfb_data("expressions")

    seen = {}
    for label, path in _scan(user_dir):
        seen[label] = path
    for label, path in _scan(system_dir):
        seen.setdefault(label, path)

    enum_items = []
    for idx, label in enumerate(sorted(seen.keys())):
        enum_items.append((seen[label], label, label, idx))
    return enum_items


_AVAILABLE_EXPRESSION_DEF = next(
    d for d in SceneConfigSet.get_definitions_in_json_directory(_PROPERTIES_DIR)
    if d.get("name") == "available_expression"
)
MakeExpressionProperties.add_property(
    _AVAILABLE_EXPRESSION_DEF,
    items_callback=_populate_available_expressions,
)

# 52 face-unit slider properties, generated dynamically from ARKIT_FACEUNITS. Each slider is a
# float in [0, 1] with a per-unit update callback that drives the matching shape key on the
# basemesh in real time.
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
    """Write a {face_unit_name: weight} dict into the slider scene properties without triggering
    the per-slider update callbacks. Caller is responsible for applying the values to the basemesh
    in bulk afterwards (typically via FaceService.set_expression)."""
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
