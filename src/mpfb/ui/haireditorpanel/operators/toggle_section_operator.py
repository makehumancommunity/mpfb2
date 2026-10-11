# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         16.9.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  folding the hair editor UI sections, without touching the scene
# ------------------------------------------------------------------------------
"""Which hair editor sections are unfolded, and the operator that flips one.

Kept in a module dict, because using property would push an undo step on each change.
Fold state is not saved with the file.
"""

from ....services.logservice import LogService
from .... import ClassManager
from ...mpfboperator import MpfbOperator

import bpy

_LOG = LogService.get_logger("haireditorpanel.toggle_section_operator")

# (asset name, section) -> unfolded. Missing key means the default of the section.
_OPEN_SECTIONS = {}


def is_open(asset_name, section, default=False):
    """Whether this asset's section is currently unfolded."""
    return _OPEN_SECTIONS.get((asset_name, section), default)


def forget_asset(asset_name):
    """Drop the fold state of an asset which is no longer there."""
    for key in [key for key in _OPEN_SECTIONS if key[0] == asset_name]:
        del _OPEN_SECTIONS[key]


class MPFB_OT_ToggleHairSection_Operator(MpfbOperator):
    """Show or hide this group of settings"""

    bl_idname = "mpfb.toggle_hair_section"
    bl_label = "Toggle section"
    bl_options = {'INTERNAL'}

    hair_asset: bpy.props.StringProperty(default="")
    section: bpy.props.StringProperty(default="")
    default_open: bpy.props.BoolProperty(default=False)

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        key = (self.hair_asset, self.section)
        _OPEN_SECTIONS[key] = not _OPEN_SECTIONS.get(key, self.default_open)
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_ToggleHairSection_Operator)
