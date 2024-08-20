import bpy, os
from pytest import approx
from .. import dynamic_import
from .. import ObjectService
from .. import NodeService
NodeWrapperMpfbValueRamp3 = dynamic_import("mpfb.entities.nodemodel.v2.composites.nodewrappermpfbvalueramp3", "NodeWrapperMpfbValueRamp3")

def test_composite_is_available():
    assert NodeWrapperMpfbValueRamp3

def test_composite_can_create_instance():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = NodeWrapperMpfbValueRamp3.create_instance(node_tree)
    assert node
    assert node.node_tree.name == "MpfbValueRamp3"
    assert "Group Input" in node.node_tree.nodes
    assert "Group Output" in node.node_tree.nodes
    assert "Map Range" in node.node_tree.nodes
    assert "Math.003" in node.node_tree.nodes
    assert "Math" in node.node_tree.nodes
    assert "Math.001" in node.node_tree.nodes
    assert "Math.002" in node.node_tree.nodes
    assert "Math.004" in node.node_tree.nodes
    assert "Math.005" in node.node_tree.nodes
    assert "Map Range.002" in node.node_tree.nodes
    assert "Math.013" in node.node_tree.nodes
    assert "Math.014" in node.node_tree.nodes
    assert "Math.015" in node.node_tree.nodes
    assert "Math.016" in node.node_tree.nodes
    assert "Math.017" in node.node_tree.nodes
    assert "Map Range.001" in node.node_tree.nodes
    assert "Math.007" in node.node_tree.nodes
    assert "Math.009" in node.node_tree.nodes
    assert "Math.008" in node.node_tree.nodes
    assert "Math.010" in node.node_tree.nodes
    assert "Math.011" in node.node_tree.nodes
    assert "Math.020" in node.node_tree.nodes
    assert "Math.019" in node.node_tree.nodes
    assert "Math.012" in node.node_tree.nodes
    assert "Math.006" in node.node_tree.nodes
    assert "Math.021" in node.node_tree.nodes
    assert "Math.018" in node.node_tree.nodes
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
    node = NodeWrapperMpfbValueRamp3.create_instance(node_tree)
    assert NodeWrapperMpfbValueRamp3.validate_tree_against_original_def()
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)
