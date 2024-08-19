"""Functionality for removing all MPFB node groups"""

from ....services import LocationService
from ....services import LogService
from ....services import NodeService
from mpfb._classmanager import ClassManager
from ...developer.developerpanel import DEVELOPER_PROPERTIES
import bpy, os, json, pprint
from string import Template

_LOG = LogService.get_logger("developer.operators.destroygroups")

class MPFB_OT_Destroy_Groups_Operator(bpy.types.Operator):
    """Remove all groups starting with mpfb"""
    bl_idname = "mpfb.destroy_groups"
    bl_label = "Destroy Groups"
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

        scene = context.scene
        node_tree = bpy.context.space_data.edit_tree

        if not node_tree:
            self.report({'ERROR'}, "Could not deduce current node tree")
            return {'FINISHED'}


        for node_tree in bpy.data.node_groups:
            if str(node_tree.name).lower().startswith("mpfb"):
                bpy.data.node_groups.remove(node_tree)

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Destroy_Groups_Operator)
