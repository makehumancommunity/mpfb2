"""Functionality for listing log levels"""

from ....services import LogService
from mpfb._classmanager import ClassManager
from ...mpfboperator import MpfbOperator
import bpy

_LOG = LogService.get_logger("developer.listloglevels")


class MPFB_OT_List_Log_Levels_Operator(MpfbOperator):
    """List log levels to the console"""
    bl_idname = "mpfb.list_log_levels"
    bl_label = "List log levels"
    bl_options = {'REGISTER'}

    def __init__(self):
        MpfbOperator.__init__(self, "developer.listloglevels")

    def hardened_execute(self, context):
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
