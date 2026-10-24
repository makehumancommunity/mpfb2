# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         21.10.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  Way to report unsuccessful background bake
# ------------------------------------------------------------------------------
"""The result of the last failed/canceled background bake of each asset, the popup announcing it and the operator dismissing it.

A background bake ends after the bake operator is gone, so it cannot use operator.report() any more.
"""

from ....services.logservice import LogService
from .... import ClassManager
from ...mpfboperator import MpfbOperator

import bpy

_LOG = LogService.get_logger("haireditorpanel.bake_result_operator")

# (basemesh name, asset name) -> {"status": ..., "messages": [(level, text), ...]}
_LAST_BAKE_RESULTS = {}

BAKE_FAILED = "FAILED"
BAKE_CANCELLED = "CANCELLED"
BAKE_ABANDONED = "ABANDONED"
BAKE_WARNINGS = "WARNINGS"

_TITLES = {
    BAKE_FAILED: "Hair bake failed",
    BAKE_CANCELLED: "Hair bake was cancelled",
    BAKE_ABANDONED: "Hair bake was abandoned",
    BAKE_WARNINGS: "Hair bake finished with warnings",
    }


def bake_result_title(status):
    return _TITLES.get(status, "Hair bake")


def remember_bake_result(basemesh_name, asset_name, status, messages):
    """Keep the outcome of a bake, so the panel can show it until the user dismisses it."""
    _LAST_BAKE_RESULTS[(basemesh_name, asset_name)] = {"status": status, "messages": list(messages)}


def last_bake_result(basemesh_name, asset_name):
    """Outcome of the last bake of this asset, or None."""
    return _LAST_BAKE_RESULTS.get((basemesh_name, asset_name))


def forget_bake_result(basemesh_name, asset_name):
    _LAST_BAKE_RESULTS.pop((basemesh_name, asset_name), None)


def forget_asset(asset_name):
    """Drop the results of an asset which is no longer there."""
    for key in [key for key in _LAST_BAKE_RESULTS if key[1] == asset_name]:
        del _LAST_BAKE_RESULTS[key]


def show_bake_result_popup(status, messages):
    """Put the result in the window. Returns whether it was shown."""
    if bpy.app.background:
        return False
    window_manager = bpy.context.window_manager
    if window_manager is None or not window_manager.windows:
        return False

    def draw(menu, _context):
        for level, text in messages:
            menu.layout.label(text=text, icon='ERROR' if level == 'ERROR' else 'INFO')

    try:
        # Called from a timer, where the context has no window for the popup to open in
        with bpy.context.temp_override(window=window_manager.windows[0]):
            window_manager.popup_menu(draw, title=bake_result_title(status), icon='ERROR')
    except Exception as e:
        _LOG.error("Could not show the bake result", e)
        return False
    return True


class MPFB_OT_DismissHairBakeResult_Operator(MpfbOperator):
    """Hide the message about the last bake of this asset"""

    bl_idname = "mpfb.dismiss_hair_bake_result"
    bl_label = "Dismiss"
    bl_options = {'INTERNAL'}

    hair_asset: bpy.props.StringProperty(default="")
    basemesh_name: bpy.props.StringProperty(default="")

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        forget_bake_result(self.basemesh_name, self.hair_asset)
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_DismissHairBakeResult_Operator)
