"""Operator for creating a template MakeTarget target."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.targetservice import TargetService
from mpfb.ui.maketarget import MakeTargetObjectProperties
from mpfb import ClassManager

_LOG = LogService.get_logger("maketarget.createtarget")

class MPFB_OT_CreateTargetOperator(bpy.types.Operator):
    """Create primary target"""
    bl_idname = "mpfb.create_maketarget_target"
    bl_label = "Create target"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if not ObjectService.object_is_basemesh(context.active_object):
            return False
        return not context.active_object.data.shape_keys

    def execute(self, context):
        blender_object = context.active_object
        TargetService.create_shape_key(blender_object, "PrimaryTarget")

        # This might look strange, but it is to ensure the name attribute of the object
        # is not still null if left at its default
        name = MakeTargetObjectProperties.get_value("name", entity_reference=blender_object)
        MakeTargetObjectProperties.set_value("name", name, entity_reference=blender_object)

        self.report({'INFO'}, "Primary target created")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_CreateTargetOperator)
