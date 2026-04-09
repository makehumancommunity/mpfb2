"""Operator for setting mesh as clothes."""

import bpy
from .....services import LogService
from .....entities.objectproperties import GeneralObjectProperties
from ..... import ClassManager
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext
from ....pollstrategy import pollstrategy, PollStrategy

_LOG = LogService.get_logger("makeclothes.markclothes")

@pollstrategy(PollStrategy.ANY_MESH_OBJECT_ACTIVE)
class MPFB_OT_MarkClothesOperator(MpfbOperator):
    """Set mesh type"""
    bl_idname = "mpfb.mark_makeclothes_clothes"
    bl_label = "Change type"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        from ...makeclothes.makeclothespanel import MAKECLOTHES_PROPERTIES  # pylint: disable=C0415
        ctx = MpfbContext(context=context, scene_properties=MAKECLOTHES_PROPERTIES)

        GeneralObjectProperties.set_value("object_type", ctx.object_type, entity_reference=ctx.active_object)

        self.report({'INFO'}, "Mesh type was set to " + ctx.object_type)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_MarkClothesOperator)
