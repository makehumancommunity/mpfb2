# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         23.9.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  flipping a bake setting toggle without pushing an undo step
# ------------------------------------------------------------------------------
"""Flip one of the bake settings, without blender pushing an undo step for it.

A property edit through a UI widget pushes an undo step and re-evaluates the depsgraph, which is slow on a character with hair.
The bake settings are only read by the bake operator, so no undo step is needed. The value is stored in the same dynamic property.
"""

from ....services.logservice import LogService
from ....services.objectservice import ObjectService
from .... import ClassManager
from ...mpfboperator import MpfbOperator
from ..hairproperties import HAIR_PROPERTIES, FUR_PROPERTIES, create_cards_bake_properties

import bpy

_LOG = LogService.get_logger("haireditorpanel.toggle_bake_flag_operator")


class MPFB_OT_ToggleBakeFlag_Operator(MpfbOperator):
    """Turn this bake setting on or off"""

    bl_idname = "mpfb.toggle_bake_flag"
    bl_label = "Toggle bake setting"
    # No 'UNDO' and no 'REGISTER'
    bl_options = {'INTERNAL'}

    hair_asset: bpy.props.StringProperty(default="")
    setting: bpy.props.StringProperty(default="")
    is_fur: bpy.props.BoolProperty(default=False)
    default_value: bpy.props.BoolProperty(default=False)

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)
        if basemesh is None:
            self.report({'ERROR'}, "Could not find basemesh amongst relatives of selected object")
            return {'CANCELLED'}
        if not self.hair_asset or not self.setting:
            self.report({'ERROR'}, "No bake setting was named")
            return {'CANCELLED'}

        properties = FUR_PROPERTIES if self.is_fur else HAIR_PROPERTIES
        name = f"{self.hair_asset}_{self.setting}"
        current = bool(properties.get_value(name, self.default_value, entity_reference=basemesh))
        try:
            properties.set_value(name, not current, entity_reference=basemesh)
        except ValueError:
            # A file saved by an older version has no definition of this setting, so create the bake settings (existing values are kept)
            _LOG.debug("The setting has no definition yet, creating the bake settings", name)
            create_cards_bake_properties(properties, basemesh, self.hair_asset)
            properties.set_value(name, not current, entity_reference=basemesh)
        _LOG.debug("Flipped a bake setting", (name, current, not current))
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_ToggleBakeFlag_Operator)
