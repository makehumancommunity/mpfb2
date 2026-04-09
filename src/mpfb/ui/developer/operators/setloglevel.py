"""Functionality for setting log levels"""

from ....services import LogService
from .... import ClassManager
from ...mpfboperator import MpfbOperator
from ...mpfbcontext import MpfbContext
import bpy

_LOG = LogService.get_logger("loglevels.operators.setloglevel")

class MPFB_OT_Set_Log_Level_Operator(MpfbOperator):
    """Set a log level override for a channel. If the "default" channel is selected, set the default log level"""
    bl_idname = "mpfb.set_log_level"
    bl_label = "Set log level"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        from ...developer.developerpanel import DEVELOPER_PROPERTIES  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=DEVELOPER_PROPERTIES)

        logger_name = ctx.available_loggers
        level_string = ctx.chosen_level

        _LOG.debug("logger name", logger_name)
        _LOG.debug("Level", level_string)

        if logger_name == "default":
            LogService.set_default_log_level(int(level_string))
        else:
            LogService.set_level_override(logger_name, int(level_string))

        self.report({"INFO"}, "Set logger " + logger_name + " to level " + LogService.LOGLEVELS[int(level_string)])

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Set_Log_Level_Operator)
