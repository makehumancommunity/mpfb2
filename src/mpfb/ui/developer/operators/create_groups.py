"""Functionality for printing a node group to the console"""

from mpfb.services.logservice import LogService
from mpfb._classmanager import ClassManager
import bpy
from string import Template

_LOG = LogService.get_logger("developer.operators.creategroups")
_LOG.set_level(LogService.DEBUG)

class MPFB_OT_Create_Groups_Operator(bpy.types.Operator):
    """Ensure v2 node trees exist."""
    bl_idname = "mpfb.create_groups"
    bl_label = "Create groups"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self, context):
        area = str(context.area.ui_type)
        if area != "ShaderNodeTree":
            _LOG.trace("Wrong context ", area)
            return False

        return True

    def execute(self, context):
        _LOG.enter()
        node_tree = bpy.context.space_data.edit_tree

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Create_Groups_Operator)
