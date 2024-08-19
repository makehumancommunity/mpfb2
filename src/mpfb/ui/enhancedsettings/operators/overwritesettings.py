
from ....services import LogService
from ....services import UiService
from ....services import LocationService
from ....services import ObjectService
from ....services import NodeService
from ....services import MaterialService
from mpfb.ui.enhancedsettings.enhancedsettingspanel import ENHANCED_SETTINGS_PROPERTIES
from mpfb._classmanager import ClassManager
import bpy, os, json

from ._savematerial import _save_material

_LOG = LogService.get_logger("enhancedsettings.overwritesettings")


class MPFB_OT_OverwriteEnhancedSettingsOperator(bpy.types.Operator):
    """This will overwrite the selected enhanced material settings, using values from the selected object's material"""
    bl_idname = "mpfb.overwrite_enhanced_settings"
    bl_label = "Overwrite settings"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have a selected object")
            return {'FINISHED'}

        name = ENHANCED_SETTINGS_PROPERTIES.get_value("available_settings", entity_reference=context)
        if not name is None:
            name = str(name).strip()
        if name == "" or name is None:
            self.report({'ERROR'}, "Settings must be chosen from the list")
            return {'FINISHED'}

        confdir = LocationService.get_user_config()
        file_name = os.path.join(confdir, "enhanced_settings." + name + ".json")

        return _save_material(self, context, file_name)

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        return not context.object is None

ClassManager.add_class(MPFB_OT_OverwriteEnhancedSettingsOperator)
