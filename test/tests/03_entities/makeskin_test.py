import bpy, os
from pytest import approx
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.services.materialservice import MaterialService
from mpfb.services.nodeservice import NodeService

def _create_object(with_material=False):
    name = ObjectService.random_name()
    mesh = bpy.data.meshes.new(name + "Mesh")
    obj = bpy.data.objects.new(name, mesh)
    if with_material:
        MaterialService.create_empty_material(name + "Material", obj)
    return obj

def test_load_mhmat_file():
    td = LocationService.get_mpfb_test("testdata")
    matfile = os.path.join(td, "materials", "notextures.mhmat")
    assert os.path.exists(matfile)
    from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
    mhmat = MakeSkinMaterial()
    assert mhmat
    mhmat.populate_from_mhmat(matfile)
    col = mhmat.get_value("diffusecolor", True)
    assert col
    assert col[0] > 0.4
    assert col[0] < 0.6

def test_basic_nodetree():
    td = LocationService.get_mpfb_test("testdata")
    matfile = os.path.join(td, "materials", "notextures.mhmat")
    from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
    mhmat = MakeSkinMaterial()
    mhmat.populate_from_mhmat(matfile)

    obj = _create_object(True)
    assert obj

    blender_material = MaterialService.get_material(obj)
    assert blender_material

    mhmat.apply_node_tree(blender_material)

    node_tree = blender_material.node_tree
    assert node_tree

    principled = NodeService.find_node_by_name(node_tree, "Principled BSDF")
    assert principled
    col = principled.inputs["Base Color"].default_value
    assert col
    assert col[0] < 0.6
    assert col[1] > 0.4

def test_most_textures():
    td = LocationService.get_mpfb_test("testdata")
    matfile = os.path.join(td, "materials", "almost_all_textures.mhmat")
    from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
    mhmat = MakeSkinMaterial()
    mhmat.populate_from_mhmat(matfile)

    obj = _create_object(True)
    assert obj

    blender_material = MaterialService.get_material(obj)
    assert blender_material

    mhmat.apply_node_tree(blender_material)

    node_tree = blender_material.node_tree
    assert node_tree

    expected_nodes = [
        "Principled BSDF",
        "diffuseTexture",
        "bumpmapTexture",
        "normalmapTexture",
        "displacementmapTexture",
        #"specularmapTexture",
        "transmissionmapTexture",
        "opacitymapTexture",
        "roughnessmapTexture",
        "metallicmapTexture",
        "aomapTexture",
        "emissionColorMapTexture",
        "emissionStrengthMapTexture",
        "subsurfaceColorMapTexture",
        "subsurfaceStrengthMapTexture",
        "bumpmap",
        "normalmap",
        "opacityMix"
        ]

    for name in expected_nodes:
        node = NodeService.find_node_by_name(node_tree, name)
        if node:
            found_name = node.name
        else:
            found_name = "not found"
        assert name == found_name

def test_specularmap():
    td = LocationService.get_mpfb_test("testdata")
    matfile = os.path.join(td, "materials", "specularmap.mhmat")
    from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
    mhmat = MakeSkinMaterial()
    mhmat.populate_from_mhmat(matfile)

    obj = _create_object(True)
    assert obj

    blender_material = MaterialService.get_material(obj)
    assert blender_material

    mhmat.apply_node_tree(blender_material)

    node_tree = blender_material.node_tree
    assert node_tree

    expected_nodes = [
        "Principled BSDF",
        "specularmapTexture",
        "specularInvert"
        ]

    for name in expected_nodes:
        node = NodeService.find_node_by_name(node_tree, name)
        if node:
            found_name = node.name
        else:
            found_name = "not found"
        assert name == found_name


