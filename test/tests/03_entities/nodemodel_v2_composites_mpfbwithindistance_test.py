import bpy, os
from pytest import approx
from mpfb.services.objectservice import ObjectService
from mpfb.services.nodeservice import NodeService
from mpfb.entities.nodemodel.v2.composites.nodewrappermpfbwithindistance import NodeWrapperMpfbWithinDistance

def test_composite_is_available():
    assert NodeWrapperMpfbWithinDistance

def test_composite_can_create_instance():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = NodeWrapperMpfbWithinDistance.create_instance(node_tree)
    assert node
    assert node.node_tree.name == "MpfbWithinDistance"
    assert "Group Output" in node.node_tree.nodes
    assert "Vector Math" in node.node_tree.nodes
    assert "Math" in node.node_tree.nodes
    assert "Group Input" in node.node_tree.nodes
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
    node = NodeWrapperMpfbWithinDistance.create_instance(node_tree)
    assert NodeWrapperMpfbWithinDistance.validate_tree_against_original_def()
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)
