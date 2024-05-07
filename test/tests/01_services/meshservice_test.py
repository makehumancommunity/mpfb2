import bpy, os, bmesh, shutil, tempfile, time
from pytest import approx
from mpfb.services.objectservice import ObjectService
from mpfb.services.humanservice import HumanService
from mpfb.services.meshservice import MeshService
from mpfb.services.locationservice import LocationService
from mpfb.entities.meshcrossref import MeshCrossRef

def test_meshservice_exists():
    """MeshService"""
    assert MeshService is not None, "MeshService can be imported"

def test_create_sample_object():
    """MeshService.create_sample_object()"""
    obj = MeshService.create_sample_object()
    assert obj is not None
    assert obj.data is not None
    assert len(obj.data.vertices) == 9
    assert len(obj.data.edges) == 12
    assert len(obj.data.polygons) == 4
    assert obj.vertex_groups.get("all")
    ObjectService.delete_object(obj)

def test_kdtree_from_human():
    """HumanService.create_human() -- defaults"""
    obj = HumanService.create_human()
    assert obj is not None
    kdtree = MeshService.get_kdtree(obj)
    assert kdtree is not None
    ObjectService.delete_object(obj)

def test_find_closest_vert():
    target_obj = HumanService.create_human()
    assert target_obj is not None
    kdtree = MeshService.get_kdtree(target_obj)
    assert kdtree is not None

    focus_obj = ObjectService.create_blender_object_with_mesh("focus_obj")
    focus_obj.location = [0.0, 0.0, 0.5]

    mesh = focus_obj.data
    bm = bmesh.new()
    bm.verts.new([0.0, 0.0, 0.0])
    bm.verts.new([0.0, 0.0, 0.5])
    bm.to_mesh(mesh)
    bm.free()

    closest = MeshService.closest_vertices(focus_obj, 1, target_obj, kdtree, 5)
    assert closest is not None
    assert len(closest) == 5

    ObjectService.delete_object(focus_obj)
    ObjectService.delete_object(target_obj)

def test_numpy_vert_coords():
    basemesh = HumanService.create_human()
    assert basemesh is not None
    coords = MeshService.get_vertex_coordinates_as_numpy_array(basemesh)
    assert coords is not None
    assert len(coords) == len(basemesh.data.vertices)
    ObjectService.delete_object(basemesh)

def test_numpy_faces():
    basemesh = HumanService.create_human()
    assert basemesh is not None
    faces = MeshService.get_faces_as_numpy_array(basemesh)
    assert faces is not None
    assert len(faces) == len(basemesh.data.polygons)
    ObjectService.delete_object(basemesh)

def test_numpy_edges():
    test_obj = MeshService.create_sample_object()
    edges = MeshService.get_edges_as_numpy_array(test_obj)
    assert len(edges) == 12
    assert len(edges) == len(test_obj.data.edges)
    ObjectService.delete_object(test_obj)

def test_crossref_basemesh_before_modifiers():
    basemesh = HumanService.create_human()
    assert basemesh is not None
    crossref = MeshService.get_mesh_cross_references(basemesh, after_modifiers=False)
    assert crossref is not None
    assert len(crossref.vertex_coordinates) == len(basemesh.data.vertices)
    assert len(crossref.faces_by_vertex) == len(basemesh.data.vertices)
    assert len(crossref.edges_by_vertex) == len(basemesh.data.vertices)
    ObjectService.delete_object(basemesh)

def test_crossref_basemesh_after_modifiers():
    basemesh = HumanService.create_human()
    assert basemesh is not None
    crossref = MeshService.get_mesh_cross_references(basemesh, after_modifiers=True)
    assert crossref is not None
    assert len(crossref.vertex_coordinates) == len(basemesh.data.vertices)
    assert len(crossref.faces_by_vertex) == len(basemesh.data.vertices)
    assert len(crossref.edges_by_vertex) == len(basemesh.data.vertices)

    ObjectService.delete_object(basemesh)

def test_crossref_basemesh_cache():

    temp_dir = tempfile.TemporaryDirectory()
    cache_dir = temp_dir.name

    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    os.makedirs(cache_dir)

    basemesh = HumanService.create_human()
    assert basemesh is not None

    assert not os.path.exists(os.path.join(cache_dir, "vertices_by_group_1.npy"))

    before = int(time.time() * 1000.0)
    crossref = MeshCrossRef(basemesh, after_modifiers=True, build_faces_by_group_reference=True, cache_dir=cache_dir, write_cache=True)
    assert crossref is not None
    after = int(time.time() * 1000.0)
    print("Building cross references without cache took", (after - before))

    uncached_coord = len(crossref.vertex_coordinates)
    uncached_vertices_by_face = len(crossref.vertices_by_face[1])
    uncached_vertices_by_group = len(crossref.vertices_by_group[1])

    assert uncached_coord > 0
    assert uncached_vertices_by_face > 0
    assert uncached_vertices_by_group > 0

    assert os.path.exists(os.path.join(cache_dir, "vertices_by_group_1.npy"))

    before = int(time.time() * 1000.0)
    crossref = MeshCrossRef(basemesh, after_modifiers=True, build_faces_by_group_reference=True, cache_dir=cache_dir, read_cache=True)
    after = int(time.time() * 1000.0)
    print("Building cross references with cache took", (after - before))

    assert crossref is not None

    cached_coord = len(crossref.vertex_coordinates)
    cached_vertices_by_face = len(crossref.vertices_by_face[1])
    cached_vertices_by_group = len(crossref.vertices_by_group[1])

    assert cached_coord == uncached_coord
    assert cached_vertices_by_face == uncached_vertices_by_face
    assert cached_vertices_by_group == uncached_vertices_by_group

    ObjectService.delete_object(basemesh)

    temp_dir.cleanup()
