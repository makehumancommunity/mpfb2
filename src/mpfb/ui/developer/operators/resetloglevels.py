"""Functionality for resetting log levels"""

from ....services import LogService
from .... import ClassManager
from ...mpfboperator import MpfbOperator
import bpy

_LOG = LogService.get_logger("loglevels.operators.resetloglevels")


class MPFB_OT_Reset_Log_Levels_Operator(MpfbOperator):
    """Reset log levels to the default. This will remove all log level overrides"""
    bl_idname = "mpfb.reset_log_levels"
    bl_label = "Reset log levels"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()
        LogService.reset_log_levels()
        self.report({"INFO"}, "All log level overrides were removed and default level was set to INFO")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Reset_Log_Levels_Operator)
