"""Operator for overwriting existing eye material settings."""

from .....services import LogService
from .....services import LocationService
from ...eyesettings.eyesettingspanel import EYE_SETTINGS_PROPERTIES
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext
import bpy, os

from ._savematerial import _save_material

_LOG = LogService.get_logger("eyesettings.overwritesettings")

@pollstrategy(PollStrategy.ANY_OBJECT_ACTIVE)
class MPFB_OT_OverwriteEyeSettingsOperator(MpfbOperator):
    """This will overwrite the selected eye material settings, using values from the selected object's material"""
    bl_idname = "mpfb.overwrite_eye_settings"
    bl_label = "Overwrite settings"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        if context.active_object is None:
            self.report({'ERROR'}, "Must have a selected object")
            return {'FINISHED'}

        ctx = MpfbContext(context=context, scene_properties=EYE_SETTINGS_PROPERTIES)
        name = ctx.available_settings
        if not name is None:
            name = str(name).strip()
        if name == "" or name is None:
            self.report({'ERROR'}, "Settings must be chosen from the list")
            return {'FINISHED'}

        confdir = LocationService.get_user_config()
        file_name = os.path.join(confdir, "eye_settings." + name + ".json")

        return _save_material(self, context, file_name)

ClassManager.add_class(MPFB_OT_OverwriteEyeSettingsOperator)
