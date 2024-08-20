import bpy, os

from .. import ObjectService
from .. import dynamic_import

GeneralObjectProperties = dynamic_import("mpfb.entities.objectproperties", "GeneralObjectProperties")

_MESH_TYPES = ("Eyes", "Eyelashes", "Eyebrows", "Tongue", "Teeth", "Hair", "Proxymeshes", "Clothes", "Basemesh")


def test_objectservice_exists():
    """ObjectService"""
    assert ObjectService is not None, "ObjectService can be imported"


def test_random_name():
    """ObjectService.random_name()"""
    assert len(ObjectService.random_name()) == 15


def test_delete_object_by_name():
    """ObjectService.delete_object_by_name()"""
    name = ObjectService.random_name()
    ObjectService.delete_object_by_name(name)  # Should not crash even when name does not exist yet
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
    ObjectService.delete_object(None)  # Ok as long as it doesn't crash


def test_object_name_exists():
    """ObjectService.name_exists()"""
    assert not ObjectService.object_name_exists(None)
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


def test_link_blender_object():
    """ObjectService.link_blender_object()"""
    name = ObjectService.random_name()
    obj = ObjectService.create_empty(name)
    assert obj is not None
    parent_name = ObjectService.random_name()
    parent_obj = ObjectService.create_empty(parent_name)
    assert parent_obj is not None
    collection = bpy.data.collections.new(ObjectService.random_name())
    assert collection is not None
    assert obj.name not in collection.all_objects
    ObjectService.link_blender_object(obj, collection=collection, parent=parent_obj)
    assert obj.name in collection.all_objects
    assert obj.parent == parent_obj
    ObjectService.delete_object_by_name(name)
    ObjectService.delete_object_by_name(parent_name)
    bpy.data.collections.remove(collection)


def test_get_list_of_children():
    """ObjectService.get_list_of_children()"""
    parent_name = ObjectService.random_name()
    parent_obj = ObjectService.create_empty(parent_name)
    objs = []
    for i in range(3):
        name = ObjectService.random_name()
        obj = ObjectService.create_empty(name)
        obj.parent = parent_obj
        objs.append(obj)
    children = ObjectService.get_list_of_children(parent_obj)
    assert children is not None
    assert len(children) > 0
    assert len(children) == len(objs)
    assert objs[1] in children
    for obj in objs:
        ObjectService.delete_object(obj)
    ObjectService.delete_object(parent_obj)

# TODO: find_by_data


def test_get_object_type():
    assert ObjectService.get_object_type(None) == ""
    name = ObjectService.random_name()
    obj = ObjectService.create_empty(name)
    assert obj is not None
    assert ObjectService.get_object_type(obj) == ""
    GeneralObjectProperties.set_value("object_type", "yadayada", obj)
    assert ObjectService.get_object_type(obj) == "yadayada"
    ObjectService.delete_object(obj)


def test_object_is():
    name = ObjectService.random_name()
    obj = ObjectService.create_empty(name)
    assert obj is not None
    assert not ObjectService.object_is(obj, "")
    assert not ObjectService.object_is(obj, "-")
    GeneralObjectProperties.set_value("object_type", "yadayada", obj)
    assert not ObjectService.object_is(obj, "-")
    for meshtype in _MESH_TYPES:
        GeneralObjectProperties.set_value("object_type", meshtype, obj)
        assert ObjectService.object_is(obj, meshtype)
    GeneralObjectProperties.set_value("object_type", "    Clothes  ", obj)
    assert ObjectService.object_is(obj, [" clothes ", "   hair"])
    ObjectService.delete_object(obj)

# TODO: object_is_skeleton, subrig, any skeleton


def test_object_is_submethods():
    name = ObjectService.random_name()
    obj = ObjectService.create_blender_object_with_mesh(name)
    assert not ObjectService.object_is_any_makehuman_mesh(obj)
    assert not ObjectService.object_is_any_mesh_asset(obj)
    assert not ObjectService.object_is_any_makehuman_object(obj)
    GeneralObjectProperties.set_value("object_type", "Eyes", obj)
    assert ObjectService.object_is_eyes(obj)
    assert ObjectService.object_is_any_mesh_asset(obj)
    assert ObjectService.object_is_any_makehuman_mesh(obj)
    assert ObjectService.object_is_any_makehuman_object(obj)
    assert not ObjectService.object_is_basemesh_or_body_proxy(obj)
    GeneralObjectProperties.set_value("object_type", "Proxymeshes", obj)
    assert not ObjectService.object_is_basemesh(obj)
    assert ObjectService.object_is_body_proxy(obj)
    assert ObjectService.object_is_any_mesh(obj)
    assert ObjectService.object_is_any_mesh_asset(obj)
    assert ObjectService.object_is_any_makehuman_mesh(obj)
    assert ObjectService.object_is_any_makehuman_object(obj)
    assert ObjectService.object_is_basemesh_or_body_proxy(obj)
    GeneralObjectProperties.set_value("object_type", "Basemesh", obj)
    assert ObjectService.object_is_basemesh(obj)
    assert not ObjectService.object_is_body_proxy(obj)
    assert ObjectService.object_is_any_mesh(obj)
    assert not ObjectService.object_is_any_mesh_asset(obj)
    assert ObjectService.object_is_any_makehuman_mesh(obj)
    assert ObjectService.object_is_any_makehuman_object(obj)
    assert ObjectService.object_is_basemesh_or_body_proxy(obj)
    ObjectService.delete_object(obj)
    name = ObjectService.random_name()
    obj = ObjectService.create_empty(name)
    assert not ObjectService.object_is_any_makehuman_mesh(obj)
    assert not ObjectService.object_is_any_mesh(obj)
    assert not ObjectService.object_is_any_mesh_asset(obj)
    assert not ObjectService.object_is_any_makehuman_object(obj)
    GeneralObjectProperties.set_value("object_type", "Eyes", obj)
    assert ObjectService.object_is_any_makehuman_object(obj)
    ObjectService.delete_object(obj)


def test_find_object_of_type_amongst_nearest_relatives():
    basemesh = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Basemesh", basemesh)
    clothes1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Clothes", clothes1)
    clothes2 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Clothes", clothes2)
    rig = ObjectService.create_empty(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Skeleton", rig)
    clothes1.parent = rig
    clothes2.parent = rig
    basemesh.parent = rig
    assert not ObjectService.find_object_of_type_amongst_nearest_relatives(None, "Eyes")
    assert not ObjectService.find_object_of_type_amongst_nearest_relatives(clothes1, "Eyes")
    assert not ObjectService.find_object_of_type_amongst_nearest_relatives(clothes2, "Yadayada")
    assert ObjectService.find_object_of_type_amongst_nearest_relatives(clothes1, "Basemesh") == basemesh
    assert ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Basemesh") == basemesh
    assert ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Clothes")
    assert not ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Clothes", only_parents=True)
    assert ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Basemesh", only_parents=True) == basemesh
    assert not ObjectService.find_object_of_type_amongst_nearest_relatives(clothes1, "Basemesh", only_children=True)
    assert ObjectService.find_object_of_type_amongst_nearest_relatives(rig, "Basemesh", only_children=True)
    assert not ObjectService.find_object_of_type_amongst_nearest_relatives(rig, "Basemesh", only_parents=True)
    assert len(list(ObjectService.find_all_objects_of_type_amongst_nearest_relatives(basemesh, "Clothes"))) == 2
    ObjectService.delete_object(basemesh)
    ObjectService.delete_object(clothes1)
    ObjectService.delete_object(clothes2)
    ObjectService.delete_object(rig)


def test_load_base_mesh():
    basemesh = ObjectService.load_base_mesh()
    assert basemesh is not None
    assert ObjectService.object_is_basemesh(basemesh)
    # TODO: Tests for scale, vertex groups
    ObjectService.delete_object(basemesh)


def test_get_selected_objects():
    non_mh_mesh_1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    mh_mesh_1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    non_mh_mesh_2 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())

    non_mh_armature_1 = ObjectService.create_blender_object_with_armature(ObjectService.random_name())
    mh_armature_1 = ObjectService.create_blender_object_with_armature(ObjectService.random_name())
    non_mh_armature_2 = ObjectService.create_blender_object_with_armature(ObjectService.random_name())

    GeneralObjectProperties.set_value("object_type", "Eyes", mh_mesh_1)
    GeneralObjectProperties.set_value("object_type", "Skeleton", mh_armature_1)

    ObjectService.deselect_and_deactivate_all()
    selected_objects = ObjectService.get_selected_objects()
    assert len(selected_objects) == 0

    non_mh_mesh_1.select_set(True)
    non_mh_mesh_2.select_set(True)
    mh_mesh_1.select_set(True)
    non_mh_armature_1.select_set(True)
    non_mh_armature_2.select_set(True)
    mh_armature_1.select_set(True)

    selected_objects = ObjectService.get_selected_objects()
    assert len(selected_objects) > 0
    assert non_mh_mesh_1 in selected_objects
    assert mh_mesh_1 in selected_objects
    assert non_mh_mesh_2 in selected_objects
    assert non_mh_armature_1 in selected_objects

    selected_objects = ObjectService.get_selected_objects(exclude_non_mh_objects=True)
    assert len(selected_objects) > 0
    assert mh_mesh_1 in selected_objects
    assert non_mh_mesh_2 not in selected_objects

    selected_objects = ObjectService.get_selected_objects(exclude_mesh_objects=True)
    assert len(selected_objects) > 0
    assert mh_mesh_1 not in selected_objects
    assert non_mh_mesh_2 not in selected_objects
    assert non_mh_armature_2 in selected_objects

