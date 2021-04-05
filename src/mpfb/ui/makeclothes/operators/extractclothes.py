"""Operator for creating template clothes from base mesh helpers."""

import bpy
from mpfb.services.logservice import LogService
from mpfb import ClassManager

_LOG = LogService.get_logger("makeclothes.extractclothes")

class MPFB_OT_ExtractClothesOperator(bpy.types.Operator):
    """Extract clothes from base mesh helpers"""
    bl_idname = "mpfb.extract_makeclothes_clothes"
    bl_label = "Extract clothes"
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

        self.report({'INFO'}, "Clothes mesh was created")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ExtractClothesOperator)
