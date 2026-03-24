"""Operator for creating template clothes from base mesh helpers."""

import bpy
from .....services import LogService
from .....services import ObjectService
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy

_LOG = LogService.get_logger("makeclothes.extractclothes")

@pollstrategy(PollStrategy.ANY_MESH_OBJECT_ACTIVE)
class MPFB_OT_ExtractClothesOperator(bpy.types.Operator):
    """Extract clothes from base mesh helpers"""
    bl_idname = "mpfb.extract_makeclothes_clothes"
    bl_label = "Extract clothes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        blender_object = context.active_object
        scene = context.scene

        from ...makeclothes.makeclothespanel import MAKECLOTHES_PROPERTIES # pylint: disable=C0415
        #from ...makeclothes import MakeClothesObjectProperties # pylint: disable=C0415

        group_name = MAKECLOTHES_PROPERTIES.get_value("available_groups", entity_reference=scene)
        ObjectService.extract_vertex_group_to_new_object(blender_object, group_name)

        self.report({'INFO'}, "Clothes mesh was created")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ExtractClothesOperator)
