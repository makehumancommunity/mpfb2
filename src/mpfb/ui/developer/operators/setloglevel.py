"""Functionality for setting log levels"""

from mpfb.services.logservice import LogService
from mpfb._classmanager import ClassManager
import bpy

_LOG = LogService.get_logger("loglevels.operators.setloglevel")


class MPFB_OT_Set_Log_Level_Operator(bpy.types.Operator):
    """Set a log level override for a channel. If the "default" channel is selected, set the default log level."""
    bl_idname = "mpfb.set_log_level"
    bl_label = "Set log level"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()

        scene = context.scene
        from mpfb.ui.developer.developerpanel import DEVELOPER_PROPERTIES # pylint: disable=C0415

        logger_name = DEVELOPER_PROPERTIES.get_value("available_loggers", entity_reference=scene)
        level_string = DEVELOPER_PROPERTIES.get_value("chosen_level", entity_reference=scene)

        _LOG.debug("logger name", logger_name)
        _LOG.debug("Level", level_string)

        if logger_name == "default":
            LogService.set_default_log_level(int(level_string))
        else:
            LogService.set_level_override(logger_name, int(level_string))

        self.report({"INFO"}, "Set logger " + logger_name + " to level " + LogService.LOGLEVELS[int(level_string)])

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Set_Log_Level_Operator)
