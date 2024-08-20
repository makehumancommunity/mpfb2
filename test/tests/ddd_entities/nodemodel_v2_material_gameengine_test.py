import bpy, os
from pytest import approx
from .. import dynamic_import
from .. import ObjectService
from .. import NodeService
from .. import LocationService
MhMaterial = dynamic_import("mpfb.entities.material.mhmaterial", "MhMaterial")
NodeWrapperGameEngine = dynamic_import("mpfb.entities.nodemodel.v2.materials.nodewrappergameengine", "NodeWrapperGameEngine")


def test_composite_is_available():
    assert NodeWrapperGameEngine


def test_composite_can_create_instance():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    td = LocationService.get_mpfb_test("testdata")
    matfile = os.path.join(td, "materials", "almost_all_textures.mhmat")
    assert os.path.exists(matfile)
    mhmat = MhMaterial()
    assert mhmat
    mhmat.populate_from_mhmat(matfile)
    NodeWrapperGameEngine.create_instance(node_tree, mhmat=mhmat)
    has_link_to_output = False
    for link in node_tree.links:
        if link.to_node.name == "Material Output":
            has_link_to_output = True
    assert has_link_to_output
    NodeService.destroy_node_tree(node_tree)


def test_composite_validate_tree():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    td = LocationService.get_mpfb_test("testdata")
    matfile = os.path.join(td, "materials", "almost_all_textures.mhmat")
    assert os.path.exists(matfile)
    mhmat = MhMaterial()
    assert mhmat
    mhmat.populate_from_mhmat(matfile)
    NodeWrapperGameEngine.create_instance(node_tree, mhmat=mhmat)
    assert NodeWrapperGameEngine.validate_tree_against_original_def(fail_hard=False, node_tree=node_tree)
    NodeService.destroy_node_tree(node_tree)
