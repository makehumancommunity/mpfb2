"""Operator for adding a rigify rig."""

import bpy

from ....services import HumanService
from ....services import LogService
from ....services import ObjectService
from ....services import SystemService
from mpfb import ClassManager

_LOG = LogService.get_logger("addrig.add_rigify_rig")

class MPFB_OT_AddRigifyRigOperator(bpy.types.Operator):
    """Add a rigify rig"""

    bl_idname = "mpfb.add_rigify_rig"
    bl_label = "Add rigify rig"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            return ObjectService.object_is_basemesh(context.active_object)
        return False

    def execute(self, context):

        if not SystemService.check_for_rigify():
            self.report({'ERROR'}, "The rigify addon isn't enabled. You need to enable it under preferences.")
            return {'FINISHED'}

        scene = context.scene

        if not ObjectService.object_is_basemesh(context.active_object):
            self.report({'ERROR'}, "Rigs can only be added to the base mesh")
            return {'FINISHED'}

        basemesh = context.active_object

        from ...addrig.addrigpanel import ADD_RIG_PROPERTIES # pylint: disable=C0415

        rigify_rig = ADD_RIG_PROPERTIES.get_value("rigify_rig", entity_reference=scene)
        import_weights = ADD_RIG_PROPERTIES.get_value("import_weights_rigify", entity_reference=scene)

        HumanService.add_builtin_rig(basemesh, "rigify." + rigify_rig, import_weights=import_weights, operator=self)

        self.report({'INFO'}, "A rig was added")
        return {'FINISHED'}



ClassManager.add_class(MPFB_OT_AddRigifyRigOperator)

