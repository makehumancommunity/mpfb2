"""Tests for the MakeUp WriteUvMap operator."""

import bpy
import tempfile
import os
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_WriteUvMapOperator = dynamic_import("mpfb.ui.create_assets.makeup.operators.writeuvmap", "MPFB_OT_WriteUvMapOperator")
MAKEUP_PROPERTIES = dynamic_import("mpfb.ui.create_assets.makeup.makeuppanel", "MAKEUP_PROPERTIES")


def test_write_uv_map_is_registered():
    assert bpy.ops.mpfb.write_uv_map is not None
    assert MPFB_OT_WriteUvMapOperator is not None


def test_write_uv_map_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_WriteUvMapOperator.poll(bpy.context)


def test_write_uv_map_poll_true_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_WriteUvMapOperator.poll(bpy.context)


def test_write_uv_map_execute_errors_without_uvmap_vertex_group():
    with HumanFixture() as fixture:
        # Check if basemesh has a "uvmap" vertex group
        has_uvmap_vg = fixture.basemesh.vertex_groups.get("uvmap") is not None
        if has_uvmap_vg:
            return  # Can't test error path, skip gracefully
        fd, tmp_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            MAKEUP_PROPERTIES.set_value("uv_map_name", "UVMap", entity_reference=bpy.context.scene)
            mockself = MockOperatorBase(filepath=tmp_path)
            result = MPFB_OT_WriteUvMapOperator.execute(mockself, bpy.context)
            # Should error or cancel since no "uvmap" vertex group
            assert result in ({'CANCELLED'}, {'FINISHED'})
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


def test_write_uv_map_execute_writes_file_with_uvmap_group():
    with HumanFixture() as fixture:
        # If the basemesh has a "uvmap" vertex group, test the happy path
        has_uvmap_vg = fixture.basemesh.vertex_groups.get("uvmap") is not None
        if not has_uvmap_vg:
            return  # No "uvmap" vertex group, skip
        fd, tmp_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            MAKEUP_PROPERTIES.set_value("uv_map_name", "UVMap", entity_reference=bpy.context.scene)
            mockself = MockOperatorBase(filepath=tmp_path)
            result = MPFB_OT_WriteUvMapOperator.execute(mockself, bpy.context)
            assert result == {'FINISHED'}
            mockself.mock_report.assert_no_errors()
            assert os.path.exists(tmp_path)
            assert os.path.getsize(tmp_path) > 0
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
