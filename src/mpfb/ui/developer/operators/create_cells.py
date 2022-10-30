"""Functionality for printing a node group to the console"""

from mpfb.services.logservice import LogService
from mpfb._classmanager import ClassManager
from mpfb.entities.nodemodel.cells import CellNodeManager
from mpfb.ui.developer.developerpanel import DEVELOPER_PROPERTIES
import bpy
from string import Template

_LOG = LogService.get_logger("developer.operators.createcells")
_LOG.set_level(LogService.DEBUG)

class MPFB_OT_Create_Cells_Operator(bpy.types.Operator):
    """Ensure cells are available to the current node tree """
    bl_idname = "mpfb.create_cells"
    bl_label = "Create cells"
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
        mnm = CellNodeManager(node_tree)
        _LOG.debug("Cell node manager", mnm)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Create_Cells_Operator)
