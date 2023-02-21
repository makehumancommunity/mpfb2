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

def shorten_name(original_name):
    return original_name.replace("NodeWrapperShaderNode", "sn")

def round_floats(o):
    if isinstance(o, float):
        return round(o, 4)
    if isinstance(o, dict):
        return {k: round_floats(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [round_floats(x) for x in o]
    return o

class MPFB_OT_Rewrite_Node_Types_Operator(bpy.types.Operator):
    """WARNING: this is a code generation utility and will overwrite corresponding source code files in the addon directory. Only use if you know what you are doing."""
    bl_idname = "mpfb.rewrite_node_types"
    bl_label = "Rewrite node types"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _LOG.enter()
        entities = LocationService.get_mpfb_root("entities")
        test = LocationService.get_mpfb_test("tests")
        v2 = os.path.join(entities, "nodemodel", "v2", "primitives")
        v2test = os.path.join(test, "03_entities", "nodemodel_v2_primitives_test.py")
        classes = NodeService.get_known_shader_node_classes()
        node_tree_name = ObjectService.random_name()
        node_tree = NodeService.create_node_tree(node_tree_name)
        valid_node_class_names = []
        for shaderclass in classes:
            node = node_tree.nodes.new(shaderclass.__name__)
            node_info = NodeService.get_v2_node_info(node)
            with open(os.path.join(v2, "nodewrapper" + shaderclass.__name__.lower()) + ".py", "w") as pyfile:
                try:
                    pyfile.write("import bpy, json\n\n")
                    pyfile.write("_ORIGINAL_NODE_DEF = json.loads(\"\"\"\n")
                    pyfile.write(json.dumps(round_floats(node_info), sort_keys=True, indent=4))
                    pyfile.write("\"\"\")\n\n")
                    pyfile.write("from .abstractnodewrapper import AbstractNodeWrapper\n\n")
                    pyfile.write("class _NodeWrapper" + shaderclass.__name__ + "(AbstractNodeWrapper):\n")
                    pyfile.write("    def __init__(self):\n")
                    pyfile.write("        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)\n\n")
                    pyfile.write(shorten_name("NodeWrapper" + shaderclass.__name__) + " = _NodeWrapper" + shaderclass.__name__ + "()\n")
                    valid_node_class_names.append(shaderclass.__name__)
                except Exception as e:
                    print("\n\n\n\n\n")
                    pprint(shaderclass.__name__ + str(e))
                    print("\n")
                    pprint(node_info)
            node_tree.nodes.remove(node)
        NodeService.destroy_node_tree(node_tree)
        valid_node_class_names.sort()
        with open(os.path.join(v2, "__init__.py"), "w") as pyfile:
            pyfile.write("from .abstractnodewrapper import AbstractNodeWrapper\n")
            for node_class in valid_node_class_names:
                pyfile.write("from .nodewrapper" + node_class.lower() + " import " + shorten_name("NodeWrapper" + node_class) + "\n")
            pyfile.write("\n")
            pyfile.write("PRIMITIVE_NODE_WRAPPERS = dict()\n")
            for node_class in valid_node_class_names:
                pyfile.write("PRIMITIVE_NODE_WRAPPERS[\"" + node_class+ "\"] = " + shorten_name("NodeWrapper" + node_class) + "\n")
            pyfile.write("\n__all__ = [\n")
            pyfile.write("    \"AbstractNodeWrapper\",\n")
            pyfile.write("    \"PRIMITIVE_NODE_WRAPPERS\"")
            for node_class in valid_node_class_names:
                pyfile.write(",\n    \"" + shorten_name("NodeWrapper" + node_class) + "\"")
            pyfile.write("\n]\n")

        with open(v2test, "w") as pyfile:
            pyfile.write("import bpy, os\n")
            pyfile.write("from pytest import approx\n")
            pyfile.write("from mpfb.services.objectservice import ObjectService\n")
            pyfile.write("from mpfb.services.nodeservice import NodeService\n")
            pyfile.write("from mpfb.entities.nodemodel.v2 import *\n\n")
            pyfile.write("def test_primitives_are_available():\n")
            for node_class in valid_node_class_names:
                pyfile.write("    assert " + shorten_name("NodeWrapper" + node_class) + "\n")

            for node_class in valid_node_class_names:
                pyfile.write("\ndef test_can_create_" + shorten_name("NodeWrapper" + node_class).lower() + "():\n")
                pyfile.write("    node_tree_name = ObjectService.random_name()\n")
                pyfile.write("    node_tree = NodeService.create_node_tree(node_tree_name)\n")
                pyfile.write("    node = " + shorten_name("NodeWrapper" + node_class) + ".create_instance(node_tree)\n")
                pyfile.write("    assert node\n")
                pyfile.write("    assert node.__class__.__name__ == \"" + node_class + "\"\n")
                pyfile.write("    node_tree.nodes.remove(node)\n")
                pyfile.write("    NodeService.destroy_node_tree(node_tree)\n")

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Rewrite_Node_Types_Operator)
