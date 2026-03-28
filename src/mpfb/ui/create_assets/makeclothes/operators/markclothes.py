"""Operator for setting mesh as clothes."""

import bpy
from .....services import LogService
from .....entities.objectproperties import GeneralObjectProperties
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy

_LOG = LogService.get_logger("makeclothes.markclothes")

@pollstrategy(PollStrategy.ANY_MESH_OBJECT_ACTIVE)
class MPFB_OT_MarkClothesOperator(bpy.types.Operator):
    """Set mesh type"""
    bl_idname = "mpfb.mark_makeclothes_clothes"
    bl_label = "Change type"
    bl_options = {'REGISTER'}

    def execute(self, context):

        blender_object = context.active_object
        scene = context.scene

        from ...makeclothes.makeclothespanel import MAKECLOTHES_PROPERTIES # pylint: disable=C0415
        new_type = MAKECLOTHES_PROPERTIES.get_value("object_type", entity_reference=scene)
        GeneralObjectProperties.set_value("object_type", new_type, entity_reference=blender_object)

        self.report({'INFO'}, "Mesh type was set to " + new_type)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_MarkClothesOperator)
