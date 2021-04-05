"""Operator for setting mesh as clothes."""

import bpy
from mpfb.services.logservice import LogService
from mpfb import ClassManager

_LOG = LogService.get_logger("makeclothes.markclothes")

class MPFB_OT_MarkClothesOperator(bpy.types.Operator):
    """Set mesh type to clothes"""
    bl_idname = "mpfb.mark_makeclothes_clothes"
    bl_label = "Mark as clothes"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            return context.active_object.type == "MESH"
        return False

    def execute(self, context):

        blender_object = context.active_object
        scene = context.scene

        from mpfb.ui.makeclothes.makeclothespanel import MAKECLOTHES_PROPERTIES # pylint: disable=C0415
        from mpfb.ui.makeclothes import MakeClothesObjectProperties # pylint: disable=C0415

        self.report({'INFO'}, "Mesh type was set to clothes")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_MarkClothesOperator)
