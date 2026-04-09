"""Tests for the MakeTarget WriteTarget operator."""

import bpy
import tempfile
import os
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, BasemeshWithTargetFixture

MPFB_OT_WriteTargetOperator = dynamic_import("mpfb.ui.create_assets.maketarget.operators", "MPFB_OT_WriteTargetOperator")


def test_write_target_is_registered():
    assert bpy.ops.mpfb.write_maketarget_target is not None
    assert MPFB_OT_WriteTargetOperator is not None


def test_write_target_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_WriteTargetOperator.poll(bpy.context)


def test_write_target_poll_true_with_target():
    with BasemeshWithTargetFixture() as fixture:
        assert MPFB_OT_WriteTargetOperator.poll(bpy.context)


def test_write_target_execute_writes_file():
    with BasemeshWithTargetFixture() as fixture:
        fd, tmp_path = tempfile.mkstemp(suffix=".target")
        os.close(fd)
        try:
            mockself = MockOperatorBase(filepath=tmp_path)
            result = MPFB_OT_WriteTargetOperator.hardened_execute(mockself, bpy.context)
            assert result == {'FINISHED'}
            mockself.mock_report.assert_no_errors()
            assert os.path.exists(tmp_path)
            assert os.path.getsize(tmp_path) > 0
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
