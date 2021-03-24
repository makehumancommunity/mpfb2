"""Functionality for listing log levels"""

from mpfb.services.logservice import LogService
from mpfb._classmanager import ClassManager
import bpy

_LOG = LogService.get_logger("loglevels.operators.listloglevels")


class MPFB_OT_List_Log_Levels_Operator(bpy.types.Operator):
    """List log levels to the console"""
    bl_idname = "mpfb.list_log_levels"
    bl_label = "List log levels"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()
        print("default".ljust(40, '.') + ": " + LogService.LOGLEVELS[LogService.get_default_log_level()])

        loggers = LogService.get_loggers()
        logger_names = list(loggers.keys())
        logger_names.sort()
        for name in logger_names:
            logger = loggers[name]
            level = "(default)"
            if logger.level_is_overridden:
                level = logger.level
                level = LogService.LOGLEVELS[level]
            print(name.ljust(40, '.') + ": " + level)

        self.report({"INFO"}, "Levels were printed to the console")

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_List_Log_Levels_Operator)
