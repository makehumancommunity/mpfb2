import bpy, os, bmesh, shutil, tempfile, time
from pytest import approx
from .. import dynamic_import
from .. import ObjectService
from .. import HumanService
from .. import MeshService
from .. import LocationService
MeshCrossRef = dynamic_import("mpfb.entities.meshcrossref", "MeshCrossRef")

def test_meshcrossref_exists():
    """MeshCrossRef"""
    assert MeshCrossRef is not None, "MeshCrossRef can be imported"

def test_create_crossref():
    target_obj = MeshService.create_sample_object()
    assert target_obj is not None
    target_xref = MeshService.get_mesh_cross_references(target_obj, build_faces_by_group_reference=True)
    assert target_xref is not None
    assert len(target_xref.vertex_coordinates) == 9
    assert len(target_xref.vertices_by_face) == 4
    ObjectService.delete_object(target_obj)

def test_edge_crossref():
    target_obj = MeshService.create_sample_object()
    target_xref = MeshService.get_mesh_cross_references(target_obj, build_faces_by_group_reference=True)
    assert len(target_xref.edges_by_vertex) == 9
    assert len(target_xref.edges_by_vertex[0]) == 2
    assert len(target_xref.edges_by_vertex[4]) == 4
    ObjectService.delete_object(target_obj)

