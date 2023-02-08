import bpy, os
from pytest import approx
from mpfb.services.objectservice import ObjectService
from mpfb.services.nodeservice import NodeService
from mpfb.entities.nodemodel.v2.composites.nodewrappermpfbbodysectionsrouter import NodeWrapperMpfbBodySectionsRouter

def test_composite_is_available():
    assert NodeWrapperMpfbBodySectionsRouter

def test_composite_can_create_instance():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = NodeWrapperMpfbBodySectionsRouter.create_instance(node_tree)
    assert node
    assert node.node_tree.name == "MpfbBodySectionsRouter"
    assert "Mix Shader.001" in node.node_tree.nodes
    assert "IsLips" in node.node_tree.nodes
    assert "IsAureolae" in node.node_tree.nodes
    assert "IsFace" in node.node_tree.nodes
    assert "IsFingernails" in node.node_tree.nodes
    assert "Mix Shader.003" in node.node_tree.nodes
    assert "Mix Shader" in node.node_tree.nodes
    assert "Mix Shader.002" in node.node_tree.nodes
    assert "Mix Shader.004" in node.node_tree.nodes
    assert "IsToenails" in node.node_tree.nodes
    assert "IsEars" in node.node_tree.nodes
    assert "Mix Shader.005" in node.node_tree.nodes
    assert "Mix Shader.006" in node.node_tree.nodes
    assert "Group Output" in node.node_tree.nodes
    assert "IsGenitals" in node.node_tree.nodes
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
    node = NodeWrapperMpfbBodySectionsRouter.create_instance(node_tree)
    assert NodeWrapperMpfbBodySectionsRouter.validate_tree_against_original_def()
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)
