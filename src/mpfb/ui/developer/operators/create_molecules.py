"""Functionality for printing a node group to the console"""

from mpfb.services.logservice import LogService
from mpfb._classmanager import ClassManager
from mpfb.entities.nodemodel.molecules import MoleculeNodeManager
from mpfb.ui.developer.developerpanel import DEVELOPER_PROPERTIES
import bpy
from string import Template

_LOG = LogService.get_logger("developer.operators.createmolecules")
_LOG.set_level(LogService.DEBUG)

class MPFB_OT_Create_Molecules_Operator(bpy.types.Operator):
    """Ensure molecules are available to the current node tree """
    bl_idname = "mpfb.create_molecules"
    bl_label = "Create molecules"
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
        mnm = MoleculeNodeManager(node_tree)
        _LOG.debug("Molecule node manager", mnm)
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Create_Molecules_Operator)
