"""Functionality for setting up v2 node groups"""

from ....services import LogService
from ....services import NodeService
from .... import ClassManager
from ...mpfboperator import MpfbOperator
import bpy
from string import Template

_LOG = LogService.get_logger("developer.operators.creategroups")

class MPFB_OT_Create_Groups_Operator(MpfbOperator):
    """Ensure v2 node groups exist."""
    bl_idname = "mpfb.create_groups"
    bl_label = "Create groups"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    @classmethod
    def poll(self, context):
        area = str(context.area.ui_type)
        if area != "ShaderNodeTree":
            _LOG.trace("Wrong context ", area)
            return False

        return True

    def hardened_execute(self, context):
        _LOG.enter()
        NodeService.ensure_v2_node_groups_exist(fail_on_validation=True)
        self.report({'INFO'}, "All groups should now exist")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Create_Groups_Operator)
