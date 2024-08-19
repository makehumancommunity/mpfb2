"""Operator for opening web browser"""

import webbrowser, bpy
from bpy.props import StringProperty
from ....services import LogService
from .... import ClassManager

_LOG = LogService.get_logger("webresources.webresource")

class MPFB_OT_Web_Resource_Operator(bpy.types.Operator):
    """Open web browser"""
    bl_idname = "mpfb.web_resource"
    bl_label = "Open"
    bl_options = {'REGISTER'}

    url: StringProperty(name="url", description="Address to open", default="")

    def execute(self, context):
        webbrowser.open(self.url)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Web_Resource_Operator)
