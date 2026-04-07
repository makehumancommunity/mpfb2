"""Operator for creating a template MakeTarget target."""

import bpy
from .....services import LogService
from .....services import ObjectService
from .....services import TargetService
from ...maketarget import MakeTargetObjectProperties
from ..... import ClassManager
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext, ContextFocusObject

_LOG = LogService.get_logger("maketarget.createtarget")

class MPFB_OT_CreateTargetOperator(MpfbOperator):
    """Create primary target"""
    bl_idname = "mpfb.create_maketarget_target"
    bl_label = "Create target"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    @classmethod
    def poll(cls, context):

        blender_object = context.active_object
        if blender_object is None:
            _LOG.trace("Blender object is None")
            return False

        object_type = ObjectService.get_object_type(blender_object)

        if not object_type or object_type == "Skeleton":
            _LOG.trace("Wrong object type", object_type)
            return False

        if not context.active_object.data.shape_keys:
            _LOG.trace("No shape keys", object_type)

        expected_name = MakeTargetObjectProperties.get_value("name", entity_reference=blender_object)
        if not expected_name:
            return True

        return not TargetService.has_target(blender_object, expected_name)

    def hardened_execute(self, context):
        ctx = MpfbContext(context=context, object_properties=MakeTargetObjectProperties,
                          focus_object_type=ContextFocusObject.ACTIVE)

        if not ctx.name:
            self.report({'ERROR'}, "Must specify the name of the target")
            return {'FINISHED'}

        TargetService.create_shape_key(ctx.active_object, ctx.name)

        # This might look strange, but it is to ensure the name attribute of the object
        # is not still null if left at its default
        MakeTargetObjectProperties.set_value("name", ctx.name, entity_reference=ctx.active_object)

        self.report({'INFO'}, "Primary target created")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_CreateTargetOperator)
