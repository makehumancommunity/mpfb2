"""Operator for opening dir browser"""

import bpy
from bpy.props import StringProperty
from .....services import LogService
from .....services import SystemService
from ..... import ClassManager
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("dirresources.dirresource")

class MPFB_OT_Dir_Resource_Operator(MpfbOperator):
    """Open dir browser"""
    bl_idname = "mpfb.dir_resource"
    bl_label = "Open"
    bl_options = {'REGISTER'}

    path: StringProperty(name="path", description="Path to open", default="")

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        SystemService.open_file_browser(self.path)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Dir_Resource_Operator)
