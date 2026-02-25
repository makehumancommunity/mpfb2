import bpy, bmesh, os

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


def test_select_object():
    """ObjectService.select_object()"""
    name = ObjectService.random_name()
    obj = ObjectService.create_empty(name)
    name2 = ObjectService.random_name()
    obj2 = ObjectService.create_empty(name2)
    obj2.select_set(True)
    obj.select_set(False)
    ObjectService.select_object(obj)
    assert obj.select_get(), "obj should be selected after select_object()"
    assert bpy.context.view_layer.objects.active == obj, "obj should be the active object"
    assert not obj2.select_get(), "obj2 should have been deselected by select_object()"
    ObjectService.delete_object(obj)
    ObjectService.delete_object(obj2)


def test_object_is_skeleton():
    """ObjectService.object_is_skeleton()"""
    name = ObjectService.random_name()
    obj = ObjectService.create_empty(name)
    assert not ObjectService.object_is_skeleton(obj), "Empty object without type should not be a skeleton"
    GeneralObjectProperties.set_value("object_type", "Skeleton", obj)
    assert ObjectService.object_is_skeleton(obj), "Object with type Skeleton should be a skeleton"
    GeneralObjectProperties.set_value("object_type", "Subrig", obj)
    assert not ObjectService.object_is_skeleton(obj), "Object with type Subrig should not be a skeleton"
    GeneralObjectProperties.set_value("object_type", "Basemesh", obj)
    assert not ObjectService.object_is_skeleton(obj), "Object with type Basemesh should not be a skeleton"
    ObjectService.delete_object(obj)


def test_object_is_subrig():
    """ObjectService.object_is_subrig()"""
    name = ObjectService.random_name()
    obj = ObjectService.create_empty(name)
    assert not ObjectService.object_is_subrig(obj), "Empty object without type should not be a subrig"
    GeneralObjectProperties.set_value("object_type", "Subrig", obj)
    assert ObjectService.object_is_subrig(obj), "Object with type Subrig should be a subrig"
    GeneralObjectProperties.set_value("object_type", "Skeleton", obj)
    assert not ObjectService.object_is_subrig(obj), "Object with type Skeleton should not be a subrig"
    GeneralObjectProperties.set_value("object_type", "Basemesh", obj)
    assert not ObjectService.object_is_subrig(obj), "Object with type Basemesh should not be a subrig"
    ObjectService.delete_object(obj)


def test_object_is_any_skeleton():
    """ObjectService.object_is_any_skeleton()"""
    name = ObjectService.random_name()
    obj = ObjectService.create_empty(name)
    assert not ObjectService.object_is_any_skeleton(obj), "Empty object without type should not be any skeleton"
    GeneralObjectProperties.set_value("object_type", "Skeleton", obj)
    assert ObjectService.object_is_any_skeleton(obj), "Object with type Skeleton should be any skeleton"
    GeneralObjectProperties.set_value("object_type", "Subrig", obj)
    assert ObjectService.object_is_any_skeleton(obj), "Object with type Subrig should be any skeleton"
    GeneralObjectProperties.set_value("object_type", "Basemesh", obj)
    assert not ObjectService.object_is_any_skeleton(obj), "Object with type Basemesh should not be any skeleton"
    GeneralObjectProperties.set_value("object_type", "Clothes", obj)
    assert not ObjectService.object_is_any_skeleton(obj), "Object with type Clothes should not be any skeleton"
    ObjectService.delete_object(obj)


def test_create_blender_object_with_armature():
    """ObjectService.create_blender_object_with_armature()"""
    name = ObjectService.random_name()
    obj = ObjectService.create_blender_object_with_armature(name=name)
    assert obj is not None
    assert obj.type == "ARMATURE"
    assert obj.name == name
    assert obj.data is not None
    parent_name = ObjectService.random_name()
    parent = ObjectService.create_empty(parent_name)
    child_name = ObjectService.random_name()
    child = ObjectService.create_blender_object_with_armature(name=child_name, parent=parent)
    assert child.parent == parent
    ObjectService.delete_object(obj)
    ObjectService.delete_object(child)
    ObjectService.delete_object(parent)


def test_find_by_data():
    """ObjectService.find_by_data()"""
    name = ObjectService.random_name()
    obj = ObjectService.create_blender_object_with_mesh(name=name)
    assert ObjectService.find_by_data(obj.data) == obj
    orphan_mesh = bpy.data.meshes.new(ObjectService.random_name() + "Mesh")
    assert ObjectService.find_by_data(orphan_mesh) is None
    bpy.data.meshes.remove(orphan_mesh)
    ObjectService.delete_object(obj)


def test_duplicate_blender_object():
    """ObjectService.duplicate_blender_object()"""
    assert ObjectService.duplicate_blender_object(None) is None
    name = ObjectService.random_name()
    original = ObjectService.create_blender_object_with_mesh(name=name)
    dup = ObjectService.duplicate_blender_object(original)
    assert dup is not None
    assert dup != original
    assert dup.type == original.type
    assert dup.data != original.data
    parent_name = ObjectService.random_name()
    parent = ObjectService.create_empty(parent_name)
    dup_with_parent = ObjectService.duplicate_blender_object(original, parent=parent)
    assert dup_with_parent.parent == parent
    ObjectService.delete_object(original)
    ObjectService.delete_object(dup)
    ObjectService.delete_object(dup_with_parent)
    ObjectService.delete_object(parent)


def test_has_vertex_group():
    """ObjectService.has_vertex_group()"""
    assert not ObjectService.has_vertex_group(None, "testgroup")
    name = ObjectService.random_name()
    obj = ObjectService.create_blender_object_with_mesh(name=name)
    bm = bmesh.new()
    bm.verts.new([0.0, 0.0, 0.0])
    bm.verts.new([1.0, 0.0, 0.0])
    bm.verts.new([0.0, 1.0, 0.0])
    bm.to_mesh(obj.data)
    bm.free()
    assert not ObjectService.has_vertex_group(obj, None)
    assert not ObjectService.has_vertex_group(obj, "testgroup")
    obj.vertex_groups.new(name="testgroup")
    assert ObjectService.has_vertex_group(obj, "testgroup")
    assert not ObjectService.has_vertex_group(obj, "othergroup")
    ObjectService.delete_object(obj)


def test_get_vertex_indexes_for_vertex_group():
    """ObjectService.get_vertex_indexes_for_vertex_group()"""
    assert ObjectService.get_vertex_indexes_for_vertex_group(None, "testgroup") == []
    name = ObjectService.random_name()
    obj = ObjectService.create_blender_object_with_mesh(name=name)
    bm = bmesh.new()
    bm.verts.new([0.0, 0.0, 0.0])
    bm.verts.new([1.0, 0.0, 0.0])
    bm.verts.new([0.0, 1.0, 0.0])
    bm.to_mesh(obj.data)
    bm.free()
    assert ObjectService.get_vertex_indexes_for_vertex_group(obj, None) == []
    assert ObjectService.get_vertex_indexes_for_vertex_group(obj, "testgroup") == []
    vg = obj.vertex_groups.new(name="testgroup")
    vg.add([0, 2], 1.0, 'ADD')
    indexes = ObjectService.get_vertex_indexes_for_vertex_group(obj, "testgroup")
    assert len(indexes) == 2
    assert 0 in indexes
    assert 2 in indexes
    assert 1 not in indexes
    obj.vertex_groups.new(name="emptygroup")
    assert ObjectService.get_vertex_indexes_for_vertex_group(obj, "emptygroup") == []
    ObjectService.delete_object(obj)


def test_object_is_generated_rigify_rig():
    """ObjectService.object_is_generated_rigify_rig()"""
    assert not ObjectService.object_is_generated_rigify_rig(None)
    name = ObjectService.random_name()
    arm = ObjectService.create_blender_object_with_armature(name=name)
    assert not ObjectService.object_is_generated_rigify_rig(arm)
    arm.data["rig_id"] = "test_id"
    assert ObjectService.object_is_generated_rigify_rig(arm)
    mesh_name = ObjectService.random_name()
    mesh_obj = ObjectService.create_blender_object_with_mesh(name=mesh_name)
    assert not ObjectService.object_is_generated_rigify_rig(mesh_obj)
    ObjectService.delete_object(arm)
    ObjectService.delete_object(mesh_obj)


def test_get_selected_mesh_objects():
    """ObjectService.get_selected_mesh_objects()"""
    ObjectService.deselect_and_deactivate_all()
    mesh1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    mesh2 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    arm1 = ObjectService.create_blender_object_with_armature(ObjectService.random_name())
    mesh1.select_set(True)
    mesh2.select_set(True)
    arm1.select_set(True)
    selected = ObjectService.get_selected_mesh_objects()
    assert mesh1 in selected
    assert mesh2 in selected
    assert arm1 not in selected
    assert len(selected) == 2
    ObjectService.delete_object(mesh1)
    ObjectService.delete_object(mesh2)
    ObjectService.delete_object(arm1)


def test_get_selected_armature_objects():
    """ObjectService.get_selected_armature_objects()"""
    ObjectService.deselect_and_deactivate_all()
    mesh1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    mesh2 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    arm1 = ObjectService.create_blender_object_with_armature(ObjectService.random_name())
    mesh1.select_set(True)
    mesh2.select_set(True)
    arm1.select_set(True)
    selected = ObjectService.get_selected_armature_objects()
    assert arm1 in selected
    assert mesh1 not in selected
    assert mesh2 not in selected
    assert len(selected) == 1
    ObjectService.delete_object(mesh1)
    ObjectService.delete_object(mesh2)
    ObjectService.delete_object(arm1)


def test_find_related_objects():
    """ObjectService.find_related_objects()"""
    rig = ObjectService.create_empty(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Skeleton", rig)
    basemesh = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Basemesh", basemesh)
    basemesh.parent = rig
    clothes1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Clothes", clothes1)
    clothes1.parent = rig
    eyes1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Eyes", eyes1)
    eyes1.parent = rig
    related = list(ObjectService.find_related_objects(basemesh))
    assert basemesh in related
    assert rig in related
    assert clothes1 in related
    assert eyes1 in related
    ObjectService.delete_object(basemesh)
    ObjectService.delete_object(clothes1)
    ObjectService.delete_object(eyes1)
    ObjectService.delete_object(rig)


def test_find_related_skeletons():
    """ObjectService.find_related_skeletons()"""
    rig = ObjectService.create_empty(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Skeleton", rig)
    basemesh = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Basemesh", basemesh)
    basemesh.parent = rig
    clothes1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Clothes", clothes1)
    clothes1.parent = rig
    eyes1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Eyes", eyes1)
    eyes1.parent = rig
    skeletons = list(ObjectService.find_related_skeletons(basemesh))
    assert rig in skeletons
    assert basemesh not in skeletons
    assert clothes1 not in skeletons
    assert eyes1 not in skeletons
    ObjectService.delete_object(basemesh)
    ObjectService.delete_object(clothes1)
    ObjectService.delete_object(eyes1)
    ObjectService.delete_object(rig)


def test_find_related_mesh_base_or_assets():
    """ObjectService.find_related_mesh_base_or_assets()"""
    rig = ObjectService.create_empty(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Skeleton", rig)
    basemesh = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Basemesh", basemesh)
    basemesh.parent = rig
    clothes1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Clothes", clothes1)
    clothes1.parent = rig
    eyes1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Eyes", eyes1)
    eyes1.parent = rig
    meshes = list(ObjectService.find_related_mesh_base_or_assets(rig))
    assert basemesh in meshes
    assert clothes1 in meshes
    assert eyes1 in meshes
    assert rig not in meshes
    ObjectService.delete_object(basemesh)
    ObjectService.delete_object(clothes1)
    ObjectService.delete_object(eyes1)
    ObjectService.delete_object(rig)


def test_find_related_mesh_assets():
    """ObjectService.find_related_mesh_assets()"""
    rig = ObjectService.create_empty(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Skeleton", rig)
    basemesh = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Basemesh", basemesh)
    basemesh.parent = rig
    clothes1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Clothes", clothes1)
    clothes1.parent = rig
    eyes1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Eyes", eyes1)
    eyes1.parent = rig
    assets = list(ObjectService.find_related_mesh_assets(basemesh))
    assert clothes1 in assets
    assert eyes1 in assets
    assert basemesh not in assets
    assert rig not in assets
    ObjectService.delete_object(basemesh)
    ObjectService.delete_object(clothes1)
    ObjectService.delete_object(eyes1)
    ObjectService.delete_object(rig)


def test_find_related_body_part_assets():
    """ObjectService.find_related_body_part_assets()"""
    rig = ObjectService.create_empty(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Skeleton", rig)
    basemesh = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Basemesh", basemesh)
    basemesh.parent = rig
    clothes1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Clothes", clothes1)
    clothes1.parent = rig
    eyes1 = ObjectService.create_blender_object_with_mesh(ObjectService.random_name())
    GeneralObjectProperties.set_value("object_type", "Eyes", eyes1)
    eyes1.parent = rig
    body_parts = list(ObjectService.find_related_body_part_assets(basemesh))
    assert eyes1 in body_parts
    assert clothes1 not in body_parts
    assert basemesh not in body_parts
    assert rig not in body_parts
    ObjectService.delete_object(basemesh)
    ObjectService.delete_object(clothes1)
    ObjectService.delete_object(eyes1)
    ObjectService.delete_object(rig)


def test_get_base_mesh_vertex_group_definition():
    """ObjectService.get_base_mesh_vertex_group_definition()"""
    groups = ObjectService.get_base_mesh_vertex_group_definition()
    assert groups is not None
    assert isinstance(groups, dict)
    assert len(groups) > 0
    assert isinstance(list(groups.values())[0], list)
    groups2 = ObjectService.get_base_mesh_vertex_group_definition()
    assert groups == groups2
    assert groups is not groups2


def test_get_face_to_vertex_table():
    """ObjectService.get_face_to_vertex_table()"""
    table = ObjectService.get_face_to_vertex_table()
    assert table is not None
    assert len(table) > 0


def test_get_vertex_to_face_table():
    """ObjectService.get_vertex_to_face_table()"""
    table = ObjectService.get_vertex_to_face_table()
    assert table is not None
    assert len(table) > 0

