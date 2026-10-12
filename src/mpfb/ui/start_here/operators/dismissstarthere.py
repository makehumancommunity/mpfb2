"""Operator for hiding the start here panel"""

from ....services import LogService
from .... import ClassManager
from .... import set_preference
from ...mpfboperator import MpfbOperator

_LOG = LogService.get_logger("start_here.dismissstarthere")


class MPFB_OT_Dismiss_Start_Here_Operator(MpfbOperator):
    """Hide the "Start here" panel. You can bring it back from the MPFB addon preferences"""
    bl_idname = "mpfb.dismiss_start_here"
    bl_label = "Don't show this again"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        set_preference("mpfb_show_start_here", False)
        self.report({'INFO'}, "The start here panel is now hidden. You can bring it back under Preferences -> Add-ons -> MPFB.")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Dismiss_Start_Here_Operator)
