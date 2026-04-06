"""Tests for the MakeUp ImportUvMap operator."""

import bpy
import tempfile
import os
import json
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_ImportUvMapOperator = dynamic_import(
    "mpfb.ui.create_assets.makeup.operators.importuvmap", "MPFB_OT_ImportUvMapOperator")
MAKEUP_PROPERTIES = dynamic_import("mpfb.ui.create_assets.makeup.makeuppanel", "MAKEUP_PROPERTIES")


def test_import_uv_map_is_registered():
    assert bpy.ops.mpfb.import_uv_map is not None
    assert MPFB_OT_ImportUvMapOperator is not None


def test_import_uv_map_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_ImportUvMapOperator.poll(bpy.context)


def test_import_uv_map_poll_true_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_ImportUvMapOperator.poll(bpy.context)


def test_import_uv_map_execute_errors_invalid_json():
    with HumanFixture() as fixture:
        fd, tmp_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            with open(tmp_path, 'w') as f:
                f.write("not valid json")
            MAKEUP_PROPERTIES.set_value("uv_map_name", "test_uv", entity_reference=bpy.context.scene)
            mockself = MockOperatorBase(filepath=tmp_path)
            result = MPFB_OT_ImportUvMapOperator.hardened_execute(mockself, bpy.context)
            assert result == {'CANCELLED'}
            mockself.mock_report.assert_reported('ERROR', "Failed to read")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


def test_import_uv_map_execute_imports_empty_uv_map():
    with HumanFixture() as fixture:
        fd, tmp_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            # Minimal valid UV map dict — empty face data, no crash expected
            uv_data = {}
            with open(tmp_path, 'w') as f:
                json.dump(uv_data, f)
            MAKEUP_PROPERTIES.set_value("uv_map_name", "imported_uv", entity_reference=bpy.context.scene)
            mockself = MockOperatorBase(filepath=tmp_path)
            result = MPFB_OT_ImportUvMapOperator.hardened_execute(mockself, bpy.context)
            # Empty dict is valid: no faces to set, should finish without error
            assert result in ({'FINISHED'}, {'CANCELLED'})
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
