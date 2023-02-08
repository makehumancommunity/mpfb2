import bpy, os
from pytest import approx
from mpfb.services.objectservice import ObjectService
from mpfb.services.nodeservice import NodeService
from mpfb.entities.nodemodel.v2.composites.nodewrappermpfbskinmastercolor import NodeWrapperMpfbSkinMasterColor

def test_composite_is_available():
    assert NodeWrapperMpfbSkinMasterColor

def test_composite_can_create_instance():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = NodeWrapperMpfbSkinMasterColor.create_instance(node_tree)
    assert node
    assert node.node_tree.name == "MpfbSkinMasterColor"
    assert "Group Output" in node.node_tree.nodes
    assert "SkinMainMix" in node.node_tree.nodes
    assert "AureolaeMix" in node.node_tree.nodes
    assert "NavelCenterMix" in node.node_tree.nodes
    assert "LipsMix" in node.node_tree.nodes
    assert "ToenailsMix" in node.node_tree.nodes
    assert "SpotMix" in node.node_tree.nodes
    assert "SkinMainOverride" in node.node_tree.nodes
    assert "AurolaeOverride" in node.node_tree.nodes
    assert "NavelCenterOverride" in node.node_tree.nodes
    assert "LipsOverride" in node.node_tree.nodes
    assert "FingernailsMix" in node.node_tree.nodes
    assert "FingernailsOverride" in node.node_tree.nodes
    assert "ToenailsOverride" in node.node_tree.nodes
    assert "SpotOverride" in node.node_tree.nodes
    assert "EyelidOverride" in node.node_tree.nodes
    assert "EyelidMix" in node.node_tree.nodes
    assert "Mix" in node.node_tree.nodes
    assert "GenitalsMix" in node.node_tree.nodes
    assert "GenitalsOverride" in node.node_tree.nodes
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
    node = NodeWrapperMpfbSkinMasterColor.create_instance(node_tree)
    assert NodeWrapperMpfbSkinMasterColor.validate_tree_against_original_def()
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)
