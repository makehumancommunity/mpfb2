"""Operator for overwriting existing eye material settings."""

from ....services import LogService
from ....services import LocationService
from mpfb.ui.eyesettings.eyesettingspanel import EYE_SETTINGS_PROPERTIES
from mpfb._classmanager import ClassManager
import bpy, os

from ._savematerial import _save_material

_LOG = LogService.get_logger("eyesettings.overwritesettings")


class MPFB_OT_OverwriteEyeSettingsOperator(bpy.types.Operator):
    """This will overwrite the selected eye material settings, using values from the selected object's material"""
    bl_idname = "mpfb.overwrite_eye_settings"
    bl_label = "Overwrite settings"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have a selected object")
            return {'FINISHED'}

        name = EYE_SETTINGS_PROPERTIES.get_value("available_settings", entity_reference=context)
        if not name is None:
            name = str(name).strip()
        if name == "" or name is None:
            self.report({'ERROR'}, "Settings must be chosen from the list")
            return {'FINISHED'}

        confdir = LocationService.get_user_config()
        file_name = os.path.join(confdir, "eye_settings." + name + ".json")

        return _save_material(self, context, file_name)

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        return not context.object is None

ClassManager.add_class(MPFB_OT_OverwriteEyeSettingsOperator)
