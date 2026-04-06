"""Functionality for replacing a node tree with v2 skin"""

from ....services import LocationService
from ....services import LogService
from ....services import NodeService
from ....entities.nodemodel.v2.materials import NodeWrapperSkin
from .... import ClassManager
from ...developer.developerpanel import DEVELOPER_PROPERTIES
from ...mpfboperator import MpfbOperator
import bpy, os, json, pprint
from string import Template

_LOG = LogService.get_logger("developer.operators.replacewithskin")

class MPFB_OT_Replace_With_Skin_Operator(MpfbOperator):
    """Wipe current node tree and insert v2 skin material"""
    bl_idname = "mpfb.replace_with_skin"
    bl_label = "Skin"
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

        node_tree = bpy.context.space_data.edit_tree

        if not node_tree:
            self.report({'ERROR'}, "Could not deduce current node tree")
            return {'FINISHED'}

        NodeWrapperSkin.create_instance(node_tree)

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Replace_With_Skin_Operator)
