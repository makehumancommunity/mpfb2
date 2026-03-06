"""Operator for loading facial shape key packs onto a basemesh."""

from ....services import LogService
from ....services import FaceService
from ....services import ObjectService
from ...mpfboperator import MpfbOperator
from .... import ClassManager

_LOG = LogService.get_logger("faceops.loadfaceshapekeys")


class MPFB_OT_Load_Face_Shape_Keys_Operator(MpfbOperator):
    """Load selected facial shape key packs onto the basemesh"""
    bl_idname = "mpfb.load_face_shape_keys"
    bl_label = "Load face shape keys"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)
        return basemesh is not None

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)
        if basemesh is None:
            self.report({'ERROR'}, "Could not find a basemesh")
            return {'FINISHED'}

        from ..faceopspanel import FACEOPS_PROPERTIES
        scene = context.scene
        visemes01 = FACEOPS_PROPERTIES.get_value("visemes01", entity_reference=scene)
        visemes02 = FACEOPS_PROPERTIES.get_value("visemes02", entity_reference=scene)
        faceunits01 = FACEOPS_PROPERTIES.get_value("faceunits01", entity_reference=scene)

        if not visemes01 and not visemes02 and not faceunits01:
            self.report({'WARNING'}, "No shape key packs selected")
            return {'FINISHED'}

        FaceService.load_targets(
            basemesh,
            load_microsoft_visemes=visemes01,
            load_meta_visemes=visemes02,
            load_arkit_faceunits=faceunits01)

        loaded = []
        if visemes01:
            loaded.append("visemes01")
        if visemes02:
            loaded.append("visemes02")
        if faceunits01:
            loaded.append("faceunits01")

        self.report({'INFO'}, "Loaded shape key pack(s): " + ", ".join(loaded))
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Load_Face_Shape_Keys_Operator)
