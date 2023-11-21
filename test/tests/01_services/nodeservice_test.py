import bpy, os, pytest, pprint
from mpfb.services.objectservice import ObjectService
from mpfb.services.nodeservice import NodeService

def test_nodeservice_exists():
    """NodeService"""
    assert NodeService is not None, "NodeService can be imported"

def test_create_and_destroy_tree():
    name = ObjectService.random_name()
    assert name not in bpy.data.node_groups
    node_tree = NodeService.create_node_tree(name)
    assert name in bpy.data.node_groups
    NodeService.destroy_node_tree(node_tree)
    assert name not in bpy.data.node_groups

def test_get_node_info_basic():
    """NodeService.get_v2_node_class_info (basics)"""
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = node_tree.nodes.new("ShaderNodeRGB")
    assert node is not None

    node_info = NodeService.get_v2_node_info(node)
    assert node_info
    assert node_info["inputs"] is not None
    assert node_info["outputs"] is not None
    assert node_info["attributes"] is not None
    assert node_info["class"] == "ShaderNodeRGB"

    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_get_node_info_inputs():
    """NodeService.get_v2_node_class_info (inputs)"""
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    assert node is not None

    node_info = NodeService.get_v2_node_info(node)
    
    pprint.pprint(node_info)
    
    assert node_info
    assert len(node_info["inputs"]) > 0
    assert "Input_Socket_Subsurface Anisotropy" in node_info["inputs"]
    assert node_info["inputs"]["Input_Socket_Subsurface Anisotropy"]["default_value"] < 0.0001

    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

#===============================================================================
# def test_get_node_info_outputs():
#     """NodeService.get_v2_node_class_info (outputs)"""
#     node_tree_name = ObjectService.random_name()
#     node_tree = NodeService.create_node_tree(node_tree_name)
#     node = node_tree.nodes.new("ShaderNodeBsdfPrincipled")
#     assert node is not None
# 
#     node_info = NodeService.get_v2_node_info(node)
#     assert node_info
#     assert len(node_info["outputs"]) > 0
#     assert "BSDF" in node_info["outputs"]
#     assert node_info["outputs"]["BSDF"]["value_type"] == "SHADER"
# 
#     node_tree.nodes.remove(node)
#     NodeService.destroy_node_tree(node_tree)
#===============================================================================

def test_get_known_shader_node_classes():
    """NodeService.get_known_shader_node_classes()"""
    classes = NodeService.get_known_shader_node_classes()
    assert bpy.types.ShaderNodeRGB in classes
    assert bpy.types.ShaderNodeBsdfPrincipled in classes
