
from ....services import LogService
from ....services import UiService
from ....services import LocationService
from ....services import ObjectService
from ....services import NodeService
from ....services import MaterialService
from ...enhancedsettings.enhancedsettingspanel import ENHANCED_SETTINGS_PROPERTIES
from .... import ClassManager
import bpy, os, json

from ._savematerial import _save_material

_LOG = LogService.get_logger("enhancedsettings.savenewsettings")


class MPFB_OT_SaveNewEnhancedSettingsOperator(bpy.types.Operator):
    """This will save new enhanced material settings with a name from the text field above, using values from the selected object's material"""
    bl_idname = "mpfb.save_new_enhanced_settings"
    bl_label = "Save new settings"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have a selected object")
            return {'FINISHED'}

        name = ENHANCED_SETTINGS_PROPERTIES.get_value("name", entity_reference=context)
        if not name is None:
            name = str(name).strip()
        if name == "" or name is None:
            self.report({'ERROR'}, "A valid name must be given")
            return {'FINISHED'}
        if " " in str(name):
            self.report({'ERROR'}, "Enhanced material settings names should not contain spaces")
            return {'FINISHED'}

        confdir = LocationService.get_user_config()
        file_name = os.path.join(confdir, "enhanced_settings." + name + ".json")
        if os.path.exists(file_name):
            self.report({'ERROR'}, "Settings with that name already exist")
            return {'FINISHED'}

        return _save_material(self, context, file_name)

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        return not context.object is None

ClassManager.add_class(MPFB_OT_SaveNewEnhancedSettingsOperator)
