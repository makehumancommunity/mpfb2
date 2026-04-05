"""Tests for the MakeTarget WriteLibTarget operator."""

import bpy
import os
from .... import dynamic_import, ObjectService, LocationService
from ..._helpers import MockOperatorBase, BasemeshWithTargetFixture

MPFB_OT_WriteLibTargetOperator = dynamic_import("mpfb.ui.create_assets.maketarget.operators", "MPFB_OT_WriteLibTargetOperator")


def test_write_lib_target_is_registered():
    assert bpy.ops.mpfb.write_library_target is not None
    assert MPFB_OT_WriteLibTargetOperator is not None


def test_write_lib_target_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_WriteLibTargetOperator.poll(bpy.context)


def test_write_lib_target_poll_true_with_target():
    with BasemeshWithTargetFixture() as fixture:
        assert MPFB_OT_WriteLibTargetOperator.poll(bpy.context)


def test_write_lib_target_execute_writes_to_library():
    created_path = None
    try:
        with BasemeshWithTargetFixture() as fixture:
            mockself = MockOperatorBase()
            result = MPFB_OT_WriteLibTargetOperator.hardened_execute(mockself, bpy.context)
            assert result == {'FINISHED'}
            mockself.mock_report.assert_no_errors()
            created_path = os.path.join(
                LocationService.get_user_data("custom"), "test_target.target")
            assert os.path.exists(created_path)
    finally:
        if created_path and os.path.exists(created_path):
            os.remove(created_path)
