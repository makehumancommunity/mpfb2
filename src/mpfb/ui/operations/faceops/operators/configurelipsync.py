"""Operator for configuring the Lip Sync addon with visemes02 shape keys."""

from .....services import LogService
from .....services import FaceService
from .....services import ObjectService
from .....services import SystemService
from ....mpfboperator import MpfbOperator
from ..... import ClassManager

_LOG = LogService.get_logger("faceops.configurelipsync")


class MPFB_OT_Configure_Lip_Sync_Operator(MpfbOperator):
    """Map loaded visemes02 shape keys to the Lip Sync addon's property slots"""
    bl_idname = "mpfb.configure_lip_sync"
    bl_label = "Assign Lip Sync shape keys"
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

        if not SystemService.check_for_lipsync():
            self.report({'ERROR'}, "Lip sync addon is not enabled")
            return {'FINISHED'}

        try:
            missing = FaceService.configure_lip_sync(basemesh)
        except ValueError as e:
            self.report({'ERROR'}, str(e))
            return {'FINISHED'}

        if missing:
            self.report({'WARNING'}, "Lip Sync configured, but some shape keys were not found: " + ", ".join(missing))
        else:
            self.report({'INFO'}, "Lip Sync configured successfully with all visemes02 shape keys")

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Configure_Lip_Sync_Operator)
