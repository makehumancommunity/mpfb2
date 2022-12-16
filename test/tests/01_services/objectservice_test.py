import bpy, os
import util
from mpfb.services.objectservice import ObjectService

def test_objectservice_exists():
    """ObjectService"""
    assert ObjectService is not None, "ObjectService can be imported"
    
def test_object_name_exists():
    """ObjectService.name_exists()"""
    name = util.random_name()    
    assert not ObjectService.object_name_exists(name), "Named object should not exist prior to creation"    
    mesh = bpy.data.meshes.new(name + "Mesh")
    obj = bpy.data.objects.new(name, mesh)    
    assert ObjectService.object_name_exists(name), "Named object should exist after creation"    
    util.delete_object_by_name(name)    
    assert not ObjectService.object_name_exists(name), "Named object should not exist after deletion"
    
def test_ensure_unique_name():
    """ObjectService.ensure_unique_name()"""
    name = util.random_name()
    assert ObjectService.ensure_unique_name(name) == name
    mesh = bpy.data.meshes.new(name + "Mesh")
    obj = bpy.data.objects.new(name, mesh)
    assert ObjectService.ensure_unique_name(name) != name
    util.delete_object_by_name(name)    
    
def test_create_empty():
    """ObjectService.create_empty"""
    name = util.random_name()       
    obj = ObjectService.create_empty(name)
    assert obj is not None, "Empty object should have been created"
    assert obj.name == name, "Empty object should have received the given name"
    assert obj.empty_display_type == "SPHERE", "Empty object should be of display type SPHERE"
    util.delete_object_by_name(name)
    