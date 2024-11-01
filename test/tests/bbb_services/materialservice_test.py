import bpy, os

from .. import LocationService
from .. import ObjectService
from .. import MaterialService
from .. import NodeService
from .. import HumanService
from .. import dynamic_import

GeneralObjectProperties = dynamic_import("mpfb.entities.objectproperties", "GeneralObjectProperties")


def _create_human_with_makeskin_material():
    td = LocationService.get_mpfb_test("testdata")
    matfile = os.path.join(td, "materials", "almost_all_textures.mhmat")
    MakeSkinMaterial = dynamic_import("mpfb.entities.material.makeskinmaterial", "MakeSkinMaterial")
    mhmat = MakeSkinMaterial()
    mhmat.populate_from_mhmat(matfile)

    obj = HumanService.create_human()
    assert obj

    name = ObjectService.random_name()
    obj.name = name
    MaterialService.create_empty_material(name + "Material", obj)
    blender_material = MaterialService.get_material(obj)
    assert blender_material

    mhmat.apply_node_tree(blender_material)

    node_tree = blender_material.node_tree
    assert node_tree

    return obj


def _create_human_with_layered_material():
    td = LocationService.get_mpfb_test("testdata")
    matfile = os.path.join(td, "materials", "almost_all_textures.mhmat")

    obj = HumanService.create_human()
    assert obj
    name = ObjectService.random_name()
    material = MaterialService.create_v2_skin_material(name, obj, mhmat_file=matfile)
    assert material

    return obj


def _create_object(with_material=False):
    name = ObjectService.random_name()
    mesh = bpy.data.meshes.new(name + "Mesh")
    obj = bpy.data.objects.new(name, mesh)
    if with_material:
        MaterialService.create_empty_material(name + "Material", obj)
    return obj


def test_materialservice_exists():
    """MaterialService"""
    assert MaterialService is not None, "MaterialService can be imported"


def test_create_empty_material():
    """MaterialService.create_empty_material()"""
    obj = _create_object()
    assert obj
    assert MaterialService.get_material(obj) is None
    name = ObjectService.random_name()
    material = MaterialService.create_empty_material(name)
    assert material
    assert MaterialService.get_material(obj) is None
    name = ObjectService.random_name()
    material = MaterialService.create_empty_material(name, obj)
    assert material
    assert MaterialService.get_material(obj)
    ObjectService.delete_object(obj)


def test_create_v2_skin_material():
    """MaterialService.create_v2_skin_material()"""
    basemesh = HumanService.create_human()
    assert basemesh
    name = ObjectService.random_name()
    material = MaterialService.create_v2_skin_material(name, basemesh)
    assert material
    assert MaterialService.get_material(basemesh)
    assert material == MaterialService.get_material(basemesh)
    mastercolor = NodeService.find_first_group_node_by_tree_name(material.node_tree, "MpfbSkinMasterColor")
    assert mastercolor
    assert MaterialService.identify_material(material) == "layered_skin"
    ObjectService.delete_object(basemesh)


def test_identify_material():
    obj = _create_human_with_makeskin_material()
    assert obj
    material = MaterialService.get_material(obj)
    assert MaterialService.identify_material(material) == "makeskin"
    ObjectService.delete_object(obj)


def test_add_focus_nodes_makeskin():
    obj = _create_human_with_makeskin_material()
    assert obj
    material = MaterialService.get_material(obj)
    # Test might look odd, but the logic is different with 2+ materials
    assert MaterialService.get_number_of_ink_layers(material) == 0
    MaterialService.add_focus_nodes(material)
    assert MaterialService.get_number_of_ink_layers(material) == 1
    MaterialService.add_focus_nodes(material)
    assert MaterialService.get_number_of_ink_layers(material) == 2
    MaterialService.add_focus_nodes(material)
    assert MaterialService.get_number_of_ink_layers(material) == 3
    ObjectService.delete_object(obj)


def test_add_focus_nodes_layeres():
    obj = _create_human_with_layered_material()
    assert obj
    material = MaterialService.get_material(obj)
    # Test might look odd, but the logic is different with 2+ materials
    assert MaterialService.get_number_of_ink_layers(material) == 0
    MaterialService.add_focus_nodes(material)
    assert MaterialService.get_number_of_ink_layers(material) == 1
    MaterialService.add_focus_nodes(material)
    assert MaterialService.get_number_of_ink_layers(material) == 2
    MaterialService.add_focus_nodes(material)
    assert MaterialService.get_number_of_ink_layers(material) == 3
    ObjectService.delete_object(obj)
