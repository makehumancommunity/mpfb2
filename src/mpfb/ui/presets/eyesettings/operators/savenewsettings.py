"""Operator for saving new eye material settings."""

from .....services import LogService
from .....services import LocationService
from ...eyesettings.eyesettingspanel import EYE_SETTINGS_PROPERTIES
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator
import bpy, os

from ._savematerial import _save_material

_LOG = LogService.get_logger("eyesettings.savenewsettings")


@pollstrategy(PollStrategy.ANY_OBJECT_ACTIVE)
class MPFB_OT_SaveNewEyeSettingsOperator(MpfbOperator):
    """This will save new eye material settings with a name from the text field above, using values from the selected object's material"""
    bl_idname = "mpfb.save_new_eye_settings"
    bl_label = "Save new settings"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        if context.active_object is None:
            self.report({'ERROR'}, "Must have a selected object")
            return {'FINISHED'}

        from ....mpfbcontext import MpfbContext  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=EYE_SETTINGS_PROPERTIES)
        name = ctx.name
        if not name is None:
            name = str(name).strip()
        if name == "" or name is None:
            self.report({'ERROR'}, "A valid name must be given")
            return {'FINISHED'}
        if " " in str(name):
            self.report({'ERROR'}, "Eye material settings names should not contain spaces")
            return {'FINISHED'}

        confdir = LocationService.get_user_config()
        file_name = os.path.join(confdir, "eye_settings." + name + ".json")
        if os.path.exists(file_name):
            self.report({'ERROR'}, "Settings with that name already exist")
            return {'FINISHED'}

        return _save_material(self, context, file_name)

ClassManager.add_class(MPFB_OT_SaveNewEyeSettingsOperator)
