import bpy, os
from pytest import approx
from mpfb.services.objectservice import ObjectService
from mpfb.services.nodeservice import NodeService
from mpfb.entities.nodemodel.v2.composites.nodewrappermpfbcharacterinfo import NodeWrapperMpfbCharacterInfo

def test_composite_is_available():
    assert NodeWrapperMpfbCharacterInfo

def test_composite_can_create_instance():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = NodeWrapperMpfbCharacterInfo.create_instance(node_tree)
    assert node
    assert node.node_tree.name == "MpfbCharacterInfo"
    assert "Group Input" in node.node_tree.nodes
    assert "Group Output" in node.node_tree.nodes
    assert "scale_factor" in node.node_tree.nodes
    assert "gender" in node.node_tree.nodes
    assert "weight" in node.node_tree.nodes
    assert "muscle" in node.node_tree.nodes
    assert "age" in node.node_tree.nodes
    assert "height" in node.node_tree.nodes
    has_link_to_output = False
    for link in node.node_tree.links:
        if link.to_node.name == "Group Output":
            has_link_to_output = True
    assert has_link_to_output
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_composite_validate_tree():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = NodeWrapperMpfbCharacterInfo.create_instance(node_tree)
    assert NodeWrapperMpfbCharacterInfo.validate_tree_against_original_def()
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)
