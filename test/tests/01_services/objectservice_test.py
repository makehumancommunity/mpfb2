import bpy, os
from mpfb.services.objectservice import ObjectService

def test_objectservice_exists():
    """ObjectService"""
    assert ObjectService is not None, "ObjectService can be imported"

def test_random_name():
    """ObjectService.random_name()"""
    assert len(ObjectService.random_name()) == 15

def test_delete_object_by_name():
    """ObjectService.delete_object_by_name()"""
    name = ObjectService.random_name()
    ObjectService.delete_object_by_name(name) # Should not crash even when name does not exist yet
    mesh = bpy.data.meshes.new(name + "Mesh")
    obj = bpy.data.objects.new(name, mesh)
    ObjectService.delete_object_by_name(name)
    assert not ObjectService.object_name_exists(name), "Named object should not exist after deletion"

def test_delete_object():
    """ObjectService.delete_object_by_name()"""
    name = ObjectService.random_name()
    mesh = bpy.data.meshes.new(name + "Mesh")
    obj = bpy.data.objects.new(name, mesh)
    ObjectService.delete_object(obj)
    assert not ObjectService.object_name_exists(name), "Named object should not exist after deletion"
    ObjectService.delete_object(None) # Ok as long as it doesn't crash

def test_object_name_exists():
    """ObjectService.name_exists()"""
    name = ObjectService.random_name()
    assert not ObjectService.object_name_exists(name), "Named object should not exist prior to creation"
    mesh = bpy.data.meshes.new(name + "Mesh")
    obj = bpy.data.objects.new(name, mesh)
    assert ObjectService.object_name_exists(name), "Named object should exist after creation"
    ObjectService.delete_object_by_name(name)
    assert not ObjectService.object_name_exists(name), "Named object should not exist after deletion"

def test_ensure_unique_name():
    """ObjectService.ensure_unique_name()"""
    name = ObjectService.random_name()
    assert ObjectService.ensure_unique_name(name) == name
    mesh = bpy.data.meshes.new(name + "Mesh")
    obj = bpy.data.objects.new(name, mesh)
    assert ObjectService.ensure_unique_name(name) != name
    ObjectService.delete_object_by_name(name)

def test_activate_blender_object():
    """ObjectService.activate_blender_object()"""
    name2 = ObjectService.random_name()
    obj2 = ObjectService.create_empty(name2)
    obj2.select_set(True)
    assert obj2.select_get()
    name = ObjectService.random_name()
    obj = ObjectService.create_empty(name)
    assert obj is not None
    obj.select_set(False)
    bpy.context.view_layer.objects.active = None
    assert not obj.select_get()
    assert bpy.context.view_layer.objects.active is None
    ObjectService.activate_blender_object(obj, deselect_all=True)
    assert obj.select_get()
    assert bpy.context.view_layer.objects.active is not None
    assert not obj2.select_get()

def test_deselect_and_deactivate_all():
    """ObjectService.deselect_and_deactivate_all()"""
    name = ObjectService.random_name()
    obj = ObjectService.create_empty(name)
    ObjectService.activate_blender_object(obj)
    assert obj.select_get()
    assert bpy.context.view_layer.objects.active is not None
    ObjectService.deselect_and_deactivate_all()
    assert not obj.select_get()
    assert bpy.context.view_layer.objects.active is None

# TODO: has_vertex_group
# TODO: get_vertex_indexes_for_vertex_group

def test_create_blender_object_with_mesh():
    """ObjectService.create_blender_object_with_mesh()"""
    name = ObjectService.random_name()
    obj = ObjectService.create_blender_object_with_mesh(name=name)
    assert obj is not None
    assert obj.type == "MESH"
    assert obj.name == name

def test_create_empty():
    """ObjectService.create_empty"""
    name = ObjectService.random_name()
    obj = ObjectService.create_empty(name)
    assert obj is not None, "Empty object should have been created"
    assert obj.name == name, "Empty object should have received the given name"
    assert obj.empty_display_type == "SPHERE", "Empty object should be of display type SPHERE"
    ObjectService.delete_object_by_name(name)
