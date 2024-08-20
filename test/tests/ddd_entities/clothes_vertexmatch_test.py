import bpy, os, bmesh
from pytest import approx
from .. import dynamic_import
from .. import ObjectService
from .. import HumanService
from .. import MeshService
from .. import LocationService
VertexMatch = dynamic_import("mpfb.entities.clothes.vertexmatch", "VertexMatch")

# Crossref target front verts:
#
# 25  20  10  15  5
# 26  21  11  16  6
# 27  22  12  17  7
# 28  23  13  18  8
# 29  24  14  19  9

RIGHT = [
    [25, 1.0], [20, 1.0],
    [26, 1.0], [21, 1.0],
    [27, 1.0], [22, 1.0],
    [28, 1.0], [23, 1.0],
    [29, 1.0], [24, 1.0]
    ]

LEFT = [
    [15, 1.0], [5, 1.0],
    [16, 1.0], [6, 1.0],
    [17, 1.0], [7, 1.0],
    [18, 1.0], [8, 1.0],
    [19, 1.0], [9, 1.0]
    ]

MID = [
    [10, 1.0],
    [11, 1.0],
    [12, 1.0],
    [13, 1.0],
    [14, 1.0]
    ]

def _load_testdata_obj(filename):
    testdata = LocationService.get_mpfb_test("testdata")
    filepath = os.path.join(testdata, filename)
    return ObjectService.load_wavefront_file(filepath)

def _create_target_mesh():
    obj = _load_testdata_obj("crossref_target.obj")
    MeshService.create_vertex_group(obj, "right", RIGHT, nuke_existing_group=True)
    MeshService.create_vertex_group(obj, "left", LEFT, nuke_existing_group=True)
    MeshService.create_vertex_group(obj, "mid", MID, nuke_existing_group=True)
    vgroup = []
    for v in range(32):
        vgroup.append([v, 1.0])
    MeshService.create_vertex_group(obj, "all", vgroup, nuke_existing_group=True)
    return obj

def _create_exact_focus():
    obj = _load_testdata_obj("vertmatch_exact.obj")
    vgroup = []
    for v in range(6):
        vgroup.append([v, 1.0])
    MeshService.create_vertex_group(obj, "all", vgroup, nuke_existing_group=True)
    return obj

def _create_simple_focus():
    obj = _load_testdata_obj("vertmatch_simple_hovering.obj")
    vgroup = []
    for v in range(6):
        vgroup.append([v, 1.0])
    MeshService.create_vertex_group(obj, "all", vgroup, nuke_existing_group=True)
    return obj

def test_vertexmatch_exists():
    """VertexMatch"""
    assert VertexMatch is not None, "VertexMatch can be imported"

def test_load_testdata():
    """Check that all relevant test data is available"""
    obj = _create_target_mesh()
    assert obj is not None
    ObjectService.delete_object(obj)

    obj = _create_exact_focus()
    assert obj is not None
    ObjectService.delete_object(obj)

    obj = _create_simple_focus()
    assert obj is not None
    ObjectService.delete_object(obj)

def test_match_exact():
    target_obj = _create_target_mesh()
    assert target_obj is not None
    target_xref = MeshService.get_mesh_cross_references(target_obj, build_faces_by_group_reference=True)
    assert target_xref is not None

    focus_obj = _create_exact_focus()
    assert focus_obj is not None
    focus_xref = MeshService.get_mesh_cross_references(focus_obj, build_faces_by_group_reference=True)
    assert focus_xref is not None

    # Target vert 21
    # Focus vert 3

    vmatch = VertexMatch(focus_obj, 3, focus_xref, target_obj, target_xref)
    assert vmatch
    assert vmatch.final_strategy == "EXACT"
    assert vmatch.exact_match_index == 21

def test_match_simple_face():
    target_obj = _create_target_mesh()
    assert target_obj is not None
    target_xref = MeshService.get_mesh_cross_references(target_obj, build_faces_by_group_reference=True)
    assert target_xref is not None

    focus_obj = _create_simple_focus()
    assert focus_obj is not None
    focus_xref = MeshService.get_mesh_cross_references(focus_obj, build_faces_by_group_reference=True)
    assert focus_xref is not None

    vmatch = VertexMatch(focus_obj, 3, focus_xref, target_obj, target_xref)
    assert vmatch


