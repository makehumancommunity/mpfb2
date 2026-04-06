"""Operator for creating template clothes from base mesh helpers."""

import bpy
from .....services import LogService
from .....services import ObjectService
from ..... import ClassManager
from ....mpfboperator import MpfbOperator
from ....pollstrategy import pollstrategy, PollStrategy

_LOG = LogService.get_logger("makeclothes.extractclothes")

@pollstrategy(PollStrategy.ANY_MESH_OBJECT_ACTIVE)
class MPFB_OT_ExtractClothesOperator(MpfbOperator):
    """Extract clothes from base mesh helpers"""
    bl_idname = "mpfb.extract_makeclothes_clothes"
    bl_label = "Extract clothes"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        from ...makeclothes.makeclothespanel import MAKECLOTHES_PROPERTIES  # pylint: disable=C0415
        from ....mpfbcontext import MpfbContext  # pylint: disable=C0415
        ctx = MpfbContext(context=context, scene_properties=MAKECLOTHES_PROPERTIES)

        ObjectService.extract_vertex_group_to_new_object(ctx.active_object, ctx.available_groups)

        self.report({'INFO'}, "Clothes mesh was created")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ExtractClothesOperator)
