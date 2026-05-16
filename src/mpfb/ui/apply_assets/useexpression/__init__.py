"""This module provides the expressions-library panel for applying saved ARKit expressions."""

import os, bpy
from bpy.props import FloatProperty

from ....services import LogService
from ....services import ObjectService
from ....services import SceneConfigSet
from ....services import UiService
from ....services.faceservice import FaceService

_LOG = LogService.get_logger("useexpression.init")
_LOG.trace("initializing useexpression module")


# Flipped by bulk slider writes (e.g. on character load) to make the per-slider update
# callbacks no-op. Mirrors the composer's _SUPPRESS_UPDATE pattern.
_SUPPRESS_UPDATE = False


def _is_update_suppressed():
    return _SUPPRESS_UPDATE


def _set_update_suppressed(value):
    global _SUPPRESS_UPDATE
    _SUPPRESS_UPDATE = bool(value)


ExpressionsLibraryProperties = SceneConfigSet([
    {
        "type": "boolean",
        "name": "auto_refit",
        "description": "Automatically refit the human after each expression change",
        "label": "Auto refit",
        "default": True,
    },
    {
        "type": "boolean",
        "name": "only_show_applied",
        "description": "Hide sliders whose current weight is zero",
        "label": "Only show applied",
        "default": False,
    },
    {
        "type": "string",
        "name": "filter",
        "description": "Case-insensitive substring filter on the expression label",
        "label": "Filter",
        "default": "",
    },
], prefix="EXPRLIB_")


# Maps Blender scene-property identifier -> { asset, label, absolute_path }.
# Populated once at module import time below.
_EXPRESSION_PROP_MAP = {}


def _make_slider_update(identifier):
    """Build an update callback for a single expression slider."""

    def _update(self, context):
        if _is_update_suppressed():
            return
        entry = _EXPRESSION_PROP_MAP.get(identifier)
        if entry is None:
            return
        active = context.active_object if context else None
        if active is None:
            return
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(active, "Basemesh")
        if basemesh is None:
            return
        weight = getattr(self, identifier, 0.0)
        try:
            weight = float(weight)
        except (TypeError, ValueError):
            weight = 0.0
        if weight < 0.0:
            weight = 0.0
        elif weight > 1.0:
            weight = 1.0
        try:
            FaceService.set_stack_weight(basemesh, entry["asset"], weight)
            if ExpressionsLibraryProperties.get_value("auto_refit", entity_reference=context.scene):
                from ....services import HumanService  # pylint: disable=C0415
                HumanService.refit(active)
        except Exception as exc:  # pylint: disable=W0703
            _LOG.error("Failed to apply expression slider value", (identifier, weight, exc))

    return _update


def _register_expression_sliders():
    """Scan all four asset roots for expression files and register one scene float prop each."""
    _LOG.enter()
    try:
        entries = FaceService.list_available_expressions()
    except Exception as exc:  # pylint: disable=W0703
        _LOG.warn("Could not list available expressions at registration time", exc)
        return

    for abs_path, rel_path, metadata in entries:
        if not isinstance(metadata, dict):
            metadata = {}
        label = metadata.get("label") or os.path.splitext(os.path.basename(rel_path))[0].replace("_", " ")
        identifier = UiService.as_valid_identifier("expr_" + rel_path)
        if identifier in _EXPRESSION_PROP_MAP:
            continue
        _EXPRESSION_PROP_MAP[identifier] = {
            "asset": rel_path,
            "label": label,
            "absolute_path": abs_path,
        }
        prop = FloatProperty(
            name=label,
            description=metadata.get("description", "") or label,
            default=0.0,
            min=0.0,
            max=1.0,
            soft_min=0.0,
            soft_max=1.0,
            update=_make_slider_update(identifier),
        )
        setattr(bpy.types.Scene, identifier, prop)


_register_expression_sliders()


def refresh_expression_sliders(force_redraw=True):
    """Re-scan expression assets and register scene props for any new ones.

    Returns the number of newly registered sliders. The underlying registration
    is idempotent, so calling this repeatedly is safe.
    """
    _LOG.enter()
    before = len(_EXPRESSION_PROP_MAP)
    _register_expression_sliders()
    added = len(_EXPRESSION_PROP_MAP) - before

    if force_redraw and added > 0:
        try:
            wm = bpy.context.window_manager
            if wm is not None:
                for window in wm.windows:
                    screen = window.screen
                    if screen is None:
                        continue
                    for area in screen.areas:
                        if area.type == 'VIEW_3D':
                            area.tag_redraw()
        except Exception as exc:  # pylint: disable=W0703
            _LOG.warn("Could not tag VIEW_3D areas for redraw after slider refresh", exc)

    return added


def write_slider_values(scene, applied_stack):
    """Write a list of {"asset": ..., "weight": ...} rows into the registered scene props.

    Any registered slider whose asset is not in the stack is reset to 0.0. Update callbacks
    are suppressed for the duration so the write does not re-trigger the rebuild flow.
    """
    if scene is None:
        return
    weight_by_asset = {}
    for row in applied_stack or []:
        if not isinstance(row, dict):
            continue
        asset = row.get("asset")
        if not asset:
            continue
        try:
            weight_by_asset[str(asset)] = float(row.get("weight", 0.0))
        except (TypeError, ValueError):
            continue

    _set_update_suppressed(True)
    try:
        for identifier, entry in _EXPRESSION_PROP_MAP.items():
            value = weight_by_asset.get(entry["asset"], 0.0)
            if value < 0.0:
                value = 0.0
            elif value > 1.0:
                value = 1.0
            if hasattr(scene, identifier):
                setattr(scene, identifier, value)
    finally:
        _set_update_suppressed(False)


from .useexpressionpanel import MPFB_PT_ExpressionsLibrary_Panel  # noqa: E402

__all__ = [
    "MPFB_PT_ExpressionsLibrary_Panel",
    "ExpressionsLibraryProperties",
    "refresh_expression_sliders",
    "write_slider_values",
]
