import bpy, os
from pytest import approx
from mpfb.services.objectservice import ObjectService
from mpfb.services.nodeservice import NodeService
from mpfb.entities.nodemodel.v2.materials.nodewrapperskin import NodeWrapperSkin

def test_composite_is_available():
    assert NodeWrapperSkin

def test_composite_can_create_instance():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    NodeWrapperSkin.create_instance(node_tree)
    assert "Image Texture" in node_tree.nodes
    assert "Texture Coordinate" in node_tree.nodes
    assert "Material Output" in node_tree.nodes
    assert "masternormal" in node_tree.nodes
    assert "BodySectionsRouter" in node_tree.nodes
    assert "bodygroup" in node_tree.nodes
    assert "facegroup" in node_tree.nodes
    assert "earsgroup" in node_tree.nodes
    assert "lipsgroup" in node_tree.nodes
    assert "colorgroup" in node_tree.nodes
    assert "genitalsgroup" in node_tree.nodes
    assert "toenailsgroup" in node_tree.nodes
    assert "fingernailsgroup" in node_tree.nodes
    assert "aureolaegroup" in node_tree.nodes
    has_link_to_output = False
    for link in node_tree.links:
        if link.to_node.name == "Material Output":
            has_link_to_output = True
    assert has_link_to_output
    NodeService.destroy_node_tree(node_tree)

def test_composite_validate_tree():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    NodeWrapperSkin.create_instance(node_tree)
    assert NodeWrapperSkin.validate_tree_against_original_def(fail_hard=True, node_tree=node_tree)
    NodeService.destroy_node_tree(node_tree)
