"""Functionality for reconstructing the shade node type v2 model."""

from mpfb.services.locationservice import LocationService
from mpfb.services.logservice import LogService
from mpfb.services.nodeservice import NodeService
from mpfb.services.objectservice import ObjectService
from mpfb._classmanager import ClassManager
from mpfb.ui.developer.developerpanel import DEVELOPER_PROPERTIES
import bpy, os, json
from string import Template
from pprint import pprint

_LOG = LogService.get_logger("developer.operators.rewritenodetypes")
_LOG.set_level(LogService.DEBUG)

class MPFB_OT_Rewrite_Node_Types_Operator(bpy.types.Operator):
    """Generate class wrappers for basic shader node types. WARNING: this will overwrite corresponding source code in the addon directory."""
    bl_idname = "mpfb.rewrite_node_types"
    bl_label = "Rewrite node types"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()        
        entities = LocationService.get_mpfb_root("entities")
        v2 = os.path.join(entities, "nodemodel", "v2")
        classes = NodeService.get_known_shader_node_classes()
        node_tree_name = ObjectService.random_name()
        node_tree = NodeService.create_node_tree(node_tree_name)
        for shaderclass in classes:            
            node = node_tree.nodes.new(shaderclass.__name__)
            node_info = NodeService.get_v2_node_info(node)
            with open(os.path.join(v2, "nodewrapper" + shaderclass.__name__.lower()) + ".py", "w") as pyfile:
                try:
                    pyfile.write("\"\"\"\n")
                    pyfile.write(json.dumps(node_info, sort_keys=True, indent=4))
                    pyfile.write("\"\"\"\n\n")
                    pyfile.write("from .abstractnodewrapper import AbstractNodeWrapper\n\n")
                    pyfile.write("class NodeWrapper" + shaderclass.__name__ + ":\n")
                    pyfile.write("    def __init__(self):\n")
                    pyfile.write("        pass\n")
                except Exception as e:
                    print("\n\n\n\n\n")
                    pprint(shaderclass.__name__ + str(e))
                    print("\n")
                    pprint(node_info)
            node_tree.nodes.remove(node)
        NodeService.destroy_node_tree(node_tree)
            
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Rewrite_Node_Types_Operator)
