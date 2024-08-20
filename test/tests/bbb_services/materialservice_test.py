import bpy, os
from mpfb.services.objectservice import ObjectService
from mpfb.services.materialservice import MaterialService
from mpfb.services.nodeservice import NodeService
from mpfb.services.humanservice import HumanService
from mpfb.entities.objectproperties import GeneralObjectProperties

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