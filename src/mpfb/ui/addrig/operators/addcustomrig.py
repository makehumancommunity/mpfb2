"""Operator for adding a custom rig from the user library."""

import bpy

from ....services import HumanService
from ....services import LogService
from ....services import ObjectService
from .... import ClassManager

_LOG = LogService.get_logger("addrig.add_custom_rig")


class MPFB_OT_Add_Custom_Rig_Operator(bpy.types.Operator):
    """Add a custom rig from the user library to the active basemesh"""

    bl_idname = "mpfb.add_custom_rig"
    bl_label = "Add custom rig"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            return ObjectService.object_is_basemesh(context.active_object)
        return False

    def execute(self, context):
        scene = context.scene

        if not ObjectService.object_is_basemesh(context.active_object):
            self.report({'ERROR'}, "Custom rigs can only be added to the base mesh")
            return {'FINISHED'}

        basemesh = context.active_object

        from ...addrig.addrigpanel import ADD_RIG_PROPERTIES  # pylint: disable=C0415

        rig_name = ADD_RIG_PROPERTIES.get_value("custom_rig", entity_reference=scene)
        import_weights = ADD_RIG_PROPERTIES.get_value("import_weights_custom", entity_reference=scene)

        if not rig_name or rig_name == "NONE":
            self.report({'ERROR'}, "No custom rig selected")
            return {'FINISHED'}

        HumanService.add_custom_rig(basemesh, "custom." + rig_name, import_weights=import_weights, operator=self)

        self.report({'INFO'}, "Custom rig '" + rig_name + "' was added")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Add_Custom_Rig_Operator)
