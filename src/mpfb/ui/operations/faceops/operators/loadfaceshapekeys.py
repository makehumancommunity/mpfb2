"""Operator for loading facial shape key packs onto a basemesh."""

from .....services import LogService
from .....services import FaceService
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy

_LOG = LogService.get_logger("faceops.loadfaceshapekeys")

@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_Load_Face_Shape_Keys_Operator(MpfbOperator):
    """Load selected facial shape key packs onto the basemesh"""
    bl_idname = "mpfb.load_face_shape_keys"
    bl_label = "Load face shape keys"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        from ..faceopspanel import FACEOPS_PROPERTIES  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=FACEOPS_PROPERTIES)

        if ctx.basemesh is None:
            self.report({'ERROR'}, "Could not find a basemesh")
            return {'FINISHED'}

        if not ctx.visemes01 and not ctx.visemes02 and not ctx.faceunits01:
            self.report({'WARNING'}, "No shape key packs selected")
            return {'FINISHED'}

        FaceService.load_targets(
            ctx.basemesh,
            load_microsoft_visemes=ctx.visemes01,
            load_meta_visemes=ctx.visemes02,
            load_arkit_faceunits=ctx.faceunits01)

        loaded = []
        if ctx.visemes01:
            loaded.append("visemes01")
        if ctx.visemes02:
            loaded.append("visemes02")
        if ctx.faceunits01:
            loaded.append("faceunits01")

        self.report({'INFO'}, "Loaded shape key pack(s): " + ", ".join(loaded))
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Face_Shape_Keys_Operator)
