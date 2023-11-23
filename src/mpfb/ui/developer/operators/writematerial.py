"""Functionality for writing a node tree to v2 model material directory"""

from mpfb.services.locationservice import LocationService
from mpfb.services.logservice import LogService
from mpfb.services.nodeservice import NodeService
from mpfb.entities.nodemodel.v2.primitives import *
from mpfb.entities.nodemodel.v2.composites import *
from mpfb._classmanager import ClassManager
from mpfb.ui.developer.developerpanel import DEVELOPER_PROPERTIES
from .rewritenodetypes import shorten_name, round_floats
from .writecomposite import _identify_socket, _build_tree_def
import bpy, os, json, pprint
from string import Template

_LOG = LogService.get_logger("developer.operators.writematerial")

class MPFB_OT_Write_Material_Operator(bpy.types.Operator):
    """Generate the code representing a material to the materials directory"""
    bl_idname = "mpfb.write_material"
    bl_label = "Write material"
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

        output_name = DEVELOPER_PROPERTIES.get_value("output_material_name", entity_reference=scene)
        mhmat_based = DEVELOPER_PROPERTIES.get_value("mhmat_based", entity_reference=scene)

        if not output_name or not output_name.strip():
            self.report({'ERROR'}, "Must provide valid name")
            return {'FINISHED'}

        entities = LocationService.get_mpfb_root("entities")
        test = LocationService.get_mpfb_test("tests")
        v2 = os.path.join(entities, "nodemodel", "v2", "materials")
        v2test = os.path.join(test, "03_entities", "nodemodel_v2_material_" + output_name.lower() + "_test.py")

        tree_def = _build_tree_def(node_tree)

        with open(os.path.join(v2, "nodewrapper" + output_name.lower()) + ".py", "w") as pyfile:
            pyfile.write("import bpy, json\n\n")
            pyfile.write("_ORIGINAL_TREE_DEF = json.loads(\"\"\"\n")
            #pprint.pprint(tree_def)
            pyfile.write(json.dumps(tree_def, sort_keys=True, indent=4))
            pyfile.write("\"\"\")\n\n")
            pyfile.write("from .abstractmaterialwrapper import AbstractMaterialWrapper\n\n")
            pyfile.write("class _NodeWrapper" + output_name + "(AbstractMaterialWrapper):\n")
            pyfile.write("    def __init__(self):\n")
            pyfile.write("        AbstractMaterialWrapper.__init__(self, \"" + output_name + "\", _ORIGINAL_TREE_DEF)\n\n")
            if mhmat_based:
                pyfile.write("    def setup_group_nodes(self, node_tree, nodes, mhmat=None):\n\n")
                pyfile.write("        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None, mhmat_key=None):\n")
                pyfile.write("            if not mhmat_key:\n")
                pyfile.write("                nodes[name] = AbstractMaterialWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)\n")
                pyfile.write("            if mhmat_key and self.mhmat.get_value(mhmat_key):\n")
                pyfile.write("                nodes[name] = AbstractMaterialWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)\n")
                pyfile.write("                if \"Texture\" in mhmat_key:\n")
                pyfile.write("                    self.assign_mhmat_image(nodes[name], mhmat_key, mhmat)\n\n")
                pyfile.write("        def link(from_node, from_socket, to_node, to_socket, mhmat_key=None):\n")
                pyfile.write("            if not mhmat_key:\n")
                pyfile.write("                AbstractMaterialWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)\n\n")
                pyfile.write("            if mhmat_key and self.mhmat.get_value(mhmat_key):\n")
                pyfile.write("                AbstractMaterialWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)\n\n")
            else:
                pyfile.write("    def setup_group_nodes(self, node_tree, nodes, mhmat=None):\n\n")
                pyfile.write("        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):\n")
                pyfile.write("            nodes[name] = AbstractMaterialWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)\n\n")
                pyfile.write("        def link(from_node, from_socket, to_node, to_socket):\n")
                pyfile.write("            AbstractMaterialWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)\n\n")
            for node in tree_def["nodes"]:
                if node["name"] == "Material Output":
                    pyfile.write("        nodes[\"Material Output\"].location = " + str(node["attribute_values"]["location"]) + "\n")
            pyfile.write("\n")
            principled = None
            #===================================================================
            # if mhmat_based:
            #     pyfile.write("        if mhmat:\n")
            #     from mpfb.entities.material.mhmatkeys import MHMAT_KEYS
            #     for key in MHMAT_KEYS:
            #         if "Texture" in key.key_name:
            #             key_name = str(key.key_name).capitalize()
            #             pyfile.write("            has" + key_name + " = mhmat.get_value(\"" + key.key_name + "\") is not None\n")
            #     pyfile.write("\n")
            #===================================================================
            for node in tree_def["nodes"]:
                if node["class"] not in ["NodeGroupOutput", "NodeGroupInput", "ShaderNodeOutputMaterial"]:
                    if node["class"] == "ShaderNodeBsdfPrincipled":
                        principled = node["name"]
                    pyfile.write("        node(\"" + node["class"] + "\", \"" + node["name"] + "\"")
                    if node["label"] and node["label"] != node["name"]:
                        pyfile.write(", label=\"" + node["label"] + "\"")
                    if node["attribute_values"] and len(node["attribute_values"].keys()) > 0:
                        pyfile.write(", attribute_values=" + json.dumps(node["attribute_values"]).replace("true", "True").replace("false", "False"))
                    if node["input_socket_values"] and len(node["input_socket_values"].keys()) > 0:
                        pyfile.write(", input_socket_values=" + json.dumps(node["input_socket_values"]))
                    if node["output_socket_values"] and len(node["output_socket_values"].keys()) > 0:
                        pyfile.write(", output_socket_values=" + json.dumps(node["output_socket_values"]))
                    if mhmat_based:
                        pyfile.write(", mhmat_key=\"\"")
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
                    pyfile.write("\"" + link["to_socket"] + "\"")
                    if mhmat_based:
                        pyfile.write(", mhmat_key=\"\"")
                    pyfile.write(")\n")
            for link in tree_def["links"]:
                if link["to_node"] == "Group Output":
                    pyfile.write("        link(")
                    pyfile.write("\"" + link["from_node"] + "\", ")
                    pyfile.write("\"" + link["from_socket"] + "\", ")
                    pyfile.write("\"" + link["to_node"] + "\", ")
                    pyfile.write("\"" + link["to_socket"] + "\")\n")

            if principled and mhmat_based:
                pyfile.write("\n        principled = nodes[\"" + principled + "\"]\n");
                pyfile.write("        if mhmat:\n")
                pyfile.write("            diffuse_color = mhmat.get_value(\"diffuseColor\")\n")
                pyfile.write("            if diffuse_color:\n")
                pyfile.write("                if len(diffuse_color) < 4:\n")
                pyfile.write("                    diffuse_color.append(1.0)\n")
                pyfile.write("                principled.inputs[0].default_value = diffuse_color\n")

            pyfile.write("\n" + shorten_name("NodeWrapper" + output_name) + " = _NodeWrapper" + output_name+ "()\n")

        with open(v2test, "w") as pyfile:
            pyfile.write("import bpy, os\n")
            pyfile.write("from pytest import approx\n")
            pyfile.write("from mpfb.services.objectservice import ObjectService\n")
            pyfile.write("from mpfb.services.nodeservice import NodeService\n")
            if mhmat_based:
                pyfile.write("from mpfb.services.locationservice import LocationService\n")
                pyfile.write("from mpfb.entities.material.mhmaterial import MhMaterial\n")
            pyfile.write("from mpfb.entities.nodemodel.v2.materials.nodewrapper" + output_name.lower() + " import NodeWrapper" + output_name + "\n\n")
            pyfile.write("def test_composite_is_available():\n")
            pyfile.write("    assert NodeWrapper" + output_name + "\n\n")
            pyfile.write("def test_composite_can_create_instance():\n")
            pyfile.write("    node_tree_name = ObjectService.random_name()\n")
            pyfile.write("    node_tree = NodeService.create_node_tree(node_tree_name)\n")
            if mhmat_based:
                pyfile.write("    td = LocationService.get_mpfb_test(\"testdata\")\n")
                pyfile.write("    matfile = os.path.join(td, \"materials\", \"almost_all_textures.mhmat\")\n")
                pyfile.write("    assert os.path.exists(matfile)\n")
                pyfile.write("    mhmat = MhMaterial()\n")
                pyfile.write("    assert mhmat\n")
                pyfile.write("    mhmat.populate_from_mhmat(matfile)\n")
                pyfile.write("    NodeWrapper" + output_name + ".create_instance(node_tree, mhmat=mhmat)\n")
            else:
                pyfile.write("    NodeWrapper" + output_name + ".create_instance(node_tree)\n")
                for node in tree_def["nodes"]:
                    pyfile.write("    assert \"" + node["name"] + "\" in node_tree.nodes\n")

            pyfile.write("    has_link_to_output = False\n")
            pyfile.write("    for link in node_tree.links:\n")
            pyfile.write("        if link.to_node.name == \"Material Output\":\n")
            pyfile.write("            has_link_to_output = True\n")
            pyfile.write("    assert has_link_to_output\n")
            pyfile.write("    NodeService.destroy_node_tree(node_tree)\n\n")

            pyfile.write("def test_composite_validate_tree():\n")
            pyfile.write("    node_tree_name = ObjectService.random_name()\n")
            pyfile.write("    node_tree = NodeService.create_node_tree(node_tree_name)\n")
            if mhmat_based:
                pyfile.write("    NodeWrapper" + output_name + ".create_instance(node_tree, mhmat=None)\n")
                pyfile.write("    assert NodeWrapper" + output_name + ".validate_tree_against_original_def(fail_hard=False, node_tree=node_tree)\n")
            else:
                pyfile.write("    NodeWrapper" + output_name + ".create_instance(node_tree)\n")
                pyfile.write("    assert NodeWrapper" + output_name + ".validate_tree_against_original_def(fail_hard=True, node_tree=node_tree)\n")
            pyfile.write("    NodeService.destroy_node_tree(node_tree)\n")

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Write_Material_Operator)
