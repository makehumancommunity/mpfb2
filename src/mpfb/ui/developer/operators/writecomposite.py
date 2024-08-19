"""Functionality for writing a node group to v2 model composite directory"""

from ....services import LocationService
from ....services import LogService
from ....services import NodeService
from mpfb.entities.nodemodel.v2.primitives import *
from mpfb.entities.nodemodel.v2.composites import *
from mpfb._classmanager import ClassManager
from ...developer.developerpanel import DEVELOPER_PROPERTIES
from .rewritenodetypes import shorten_name, round_floats
import bpy, os, json, pprint
from string import Template

_LOG = LogService.get_logger("developer.operators.writecomposite")

def _identify_socket(all_sockets, socket):
    name_count = 0
    for s in all_sockets:
        if s.name == socket.name:
            name_count = name_count + 1
    if name_count < 2:
        return socket.name
    return socket.identifier

def _build_tree_def(node_tree):
    wrappers = dict(PRIMITIVE_NODE_WRAPPERS)
    wrappers.update(COMPOSITE_NODE_WRAPPERS)

    tree_def = dict()
    tree_def["nodes"] = []
    tree_def["links"] = []

    for node in node_tree.nodes:
        _LOG.debug("Evaluating node", node)
        node_class = node.__class__.__name__
        orig_node_class = node_class
        if node_class == "ShaderNodeGroup":
            node_class = node.node_tree.name

        node_def = dict()
        node_def["class"] = node_class
        node_def["name"] = node.name
        if node.label:
            node_def["label"] = node.label
        else:
            node_def["label"] = node.name

        if node_class in ["NodeGroupOutput", "NodeGroupInput"]:
            node_def["attribute_values"] = dict()
            node_def["input_socket_values"] = dict()
            node_def["output_socket_values"] = dict()
            node_def["attribute_values"]["location"] = list(node.location)
        else:
            if node_class not in wrappers:
                wrapperkeys = []
                for key in wrappers.keys():
                    wrapperkeys.append(str(key))
                wrapperkeys.sort()
                _LOG.error("Existing wrappers", wrapperkeys)
                _LOG.error("Faulty tree", node_tree)
                _LOG.error("Faulty node", (node, node_class, orig_node_class))
                raise NotImplementedError('Could not find wrapper for ' + node_class)
            wrapper = wrappers[node_class]
            node_def.update(wrapper.find_non_default_settings(node))

        _LOG.debug("Resulting node def", node_def)
        tree_def["nodes"].append(node_def)

    for link in node_tree.links:
        link_def = dict()
        link_def["from_node"] = link.from_node.name
        link_def["to_node"] = link.to_node.name
        link_def["from_socket"] = _identify_socket(link.from_node.outputs, link.from_socket)
        link_def["to_socket"] = _identify_socket(link.to_node.inputs, link.to_socket)
        tree_def["links"].append(link_def)

    return round_floats(tree_def)

class MPFB_OT_Write_Composite_Operator(bpy.types.Operator):
    """Generate the code representing a selected node group to the composite directory"""
    bl_idname = "mpfb.write_composite"
    bl_label = "Write composite"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self, context):
        area = str(context.area.ui_type)
        if area != "ShaderNodeTree":
            _LOG.trace("Wrong context ", area)
            return False

        selected = context.selected_nodes
        if not selected or len(selected) < 1:
            _LOG.trace("Nothing selected")
            return False

        for node in selected:
            classname = node.__class__.__name__
            _LOG.trace("Selected node class", classname)
            if classname == "ShaderNodeGroup":
                return True

        return False

    def execute(self, context):
        _LOG.enter()

        group = None
        selected = context.selected_nodes
        scene = context.scene

        if len(selected) > 1:
            self.report({'ERROR'}, "More than one node selected")
            return {'FINISHED'}

        for node in selected:
            classname = node.__class__.__name__
            _LOG.debug("Selected node class", classname)
            if classname == "ShaderNodeGroup":
                group = node

        if not group:
            self.report({'ERROR'}, "No group node selected")
            return {'FINISHED'}

        node_tree = group.node_tree
        output_name = node_tree.name

        if not output_name or not output_name.strip():
            self.report({'ERROR'}, "Could not deduce class name")
            return {'FINISHED'}

        node_info = round_floats(NodeService.get_v2_node_info(group))
        node_info["class"] = output_name

        _LOG.debug("node_info", node_info)

        entities = LocationService.get_mpfb_root("entities")
        test = LocationService.get_mpfb_test("tests")
        v2 = os.path.join(entities, "nodemodel", "v2", "composites")
        v2test = os.path.join(test, "03_entities", "nodemodel_v2_composites_" + output_name.lower() + "_test.py")

        tree_def = _build_tree_def(node_tree)

        with open(os.path.join(v2, "nodewrapper" + output_name.lower()) + ".py", "w") as pyfile:
            pyfile.write("import bpy, json\n\n")
            pyfile.write("_ORIGINAL_NODE_DEF = json.loads(\"\"\"\n")
            pyfile.write(json.dumps(node_info, sort_keys=False, indent=4))
            pyfile.write("\"\"\")\n\n")
            pyfile.write("_ORIGINAL_TREE_DEF = json.loads(\"\"\"\n")
            #pprint.pprint(tree_def)
            try:
                pyfile.write(json.dumps(tree_def, sort_keys=True, indent=4))
            except TypeError as e:
                _LOG.error("JSON serialization failed", e)
                _LOG.error("Struct", tree_def)
                pprint.pprint(tree_def)
                raise e
            pyfile.write("\"\"\")\n\n")
            pyfile.write("from .abstractgroupwrapper import AbstractGroupWrapper\n\n")
            pyfile.write("class _NodeWrapper" + output_name + "(AbstractGroupWrapper):\n")
            pyfile.write("    def __init__(self):\n")
            pyfile.write("        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)\n\n")
            pyfile.write("    def setup_group_nodes(self, node_tree, nodes):\n\n")
            pyfile.write("        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):\n")
            pyfile.write("            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)\n\n")
            pyfile.write("        def link(from_node, from_socket, to_node, to_socket):\n")
            pyfile.write("            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)\n\n")
            for node in tree_def["nodes"]:
                if node["name"] == "Group Input":
                    pyfile.write("        nodes[\"Group Input\"].location = " + str(node["attribute_values"]["location"]) + "\n")
                if node["name"] == "Group Output":
                    pyfile.write("        nodes[\"Group Output\"].location = " + str(node["attribute_values"]["location"]) + "\n")
            pyfile.write("\n")
            for node in tree_def["nodes"]:
                if node["class"] not in ["NodeGroupOutput", "NodeGroupInput"]:
                    pyfile.write("        node(\"" + node["class"] + "\", \"" + node["name"] + "\"")
                    if node["label"] and node["label"] != node["name"]:
                        pyfile.write(", label=\"" + node["label"] + "\"")
                    if node["attribute_values"] and len(node["attribute_values"].keys()) > 0:
                        pyfile.write(", attribute_values=" + json.dumps(node["attribute_values"]).replace("true", "True").replace("false", "False"))
                    if node["input_socket_values"] and len(node["input_socket_values"].keys()) > 0:
                        pyfile.write(", input_socket_values=" + json.dumps(node["input_socket_values"]))
                    if node["output_socket_values"] and len(node["output_socket_values"].keys()) > 0:
                        pyfile.write(", output_socket_values=" + json.dumps(node["output_socket_values"]))
                    pyfile.write(")\n")
            pyfile.write("\n")
            for link in tree_def["links"]:
                if link["from_node"] == "Group Input":
                    pyfile.write("        link(")
                    pyfile.write("\"" + link["from_node"] + "\", ")
                    pyfile.write("\"" + link["from_socket"] + "\", ")
                    pyfile.write("\"" + link["to_node"] + "\", ")
                    pyfile.write("\"" + link["to_socket"] + "\")\n")
            for link in tree_def["links"]:
                if link["from_node"] != "Group Input" and link["to_node"] != "Group Output":
                    pyfile.write("        link(")
                    pyfile.write("\"" + link["from_node"] + "\", ")
                    pyfile.write("\"" + link["from_socket"] + "\", ")
                    pyfile.write("\"" + link["to_node"] + "\", ")
                    pyfile.write("\"" + link["to_socket"] + "\")\n")
            for link in tree_def["links"]:
                if link["to_node"] == "Group Output":
                    pyfile.write("        link(")
                    pyfile.write("\"" + link["from_node"] + "\", ")
                    pyfile.write("\"" + link["from_socket"] + "\", ")
                    pyfile.write("\"" + link["to_node"] + "\", ")
                    pyfile.write("\"" + link["to_socket"] + "\")\n")

            pyfile.write("\n" + shorten_name("NodeWrapper" + output_name) + " = _NodeWrapper" + output_name+ "()\n")

        with open(v2test, "w") as pyfile:
            pyfile.write("import bpy, os\n")
            pyfile.write("from pytest import approx\n")
            pyfile.write("from ....services import ObjectService\n")
            pyfile.write("from ....services import NodeService\n")
            pyfile.write("from mpfb.entities.nodemodel.v2.composites.nodewrapper" + output_name.lower() + " import NodeWrapper" + output_name + "\n\n")
            pyfile.write("def test_composite_is_available():\n")
            pyfile.write("    assert NodeWrapper" + output_name + "\n\n")
            pyfile.write("def test_composite_can_create_instance():\n")
            pyfile.write("    node_tree_name = ObjectService.random_name()\n")
            pyfile.write("    node_tree = NodeService.create_node_tree(node_tree_name)\n")
            pyfile.write("    node = NodeWrapper" + output_name + ".create_instance(node_tree)\n")
            pyfile.write("    assert node\n")
            pyfile.write("    assert node.node_tree.name == \"" + output_name + "\"\n")
            for node in tree_def["nodes"]:
                pyfile.write("    assert \"" + node["name"] + "\" in node.node_tree.nodes\n")
            pyfile.write("    has_link_to_output = False\n")
            pyfile.write("    for link in node.node_tree.links:\n")
            pyfile.write("        if link.to_node.name == \"Group Output\":\n")
            pyfile.write("            has_link_to_output = True\n")
            pyfile.write("    assert has_link_to_output\n")
            pyfile.write("    node_tree.nodes.remove(node)\n")
            pyfile.write("    NodeService.destroy_node_tree(node_tree)\n\n")

            pyfile.write("def test_composite_validate_tree():\n")
            pyfile.write("    node_tree_name = ObjectService.random_name()\n")
            pyfile.write("    node_tree = NodeService.create_node_tree(node_tree_name)\n")
            pyfile.write("    node = NodeWrapper" + output_name + ".create_instance(node_tree)\n")
            pyfile.write("    assert NodeWrapper" + output_name + ".validate_tree_against_original_def()\n")
            pyfile.write("    node_tree.nodes.remove(node)\n")
            pyfile.write("    NodeService.destroy_node_tree(node_tree)\n")

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Write_Composite_Operator)
