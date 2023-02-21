"""Functionality for replacing a node tree with v2 skin"""

from mpfb.services.locationservice import LocationService
from mpfb.services.logservice import LogService
from mpfb.services.nodeservice import NodeService
from mpfb.entities.nodemodel.v2.materials import NodeWrapperSkin
from mpfb._classmanager import ClassManager
from mpfb.ui.developer.developerpanel import DEVELOPER_PROPERTIES
import bpy, os, json, pprint
from string import Template

_LOG = LogService.get_logger("developer.operators.replacewithskin")

class MPFB_OT_Replace_With_Skin_Operator(bpy.types.Operator):
    """Wipe current node tree and insert v2 skin material"""
    bl_idname = "mpfb.replace_with_skin"
    bl_label = "Skin"
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

        NodeWrapperSkin.create_instance(node_tree)

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Replace_With_Skin_Operator)
