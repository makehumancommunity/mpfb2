"""Operator for opening web browser"""

import webbrowser, bpy
from bpy.props import StringProperty
from .....services import LogService
from ..... import ClassManager
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("webresources.webresource")

class MPFB_OT_Web_Resource_Operator(MpfbOperator):
    """Open web browser"""
    bl_idname = "mpfb.web_resource"
    bl_label = "Open"
    bl_options = {'REGISTER'}

    url: StringProperty(name="url", description="Address to open", default="")

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        webbrowser.open(self.url)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Web_Resource_Operator)
