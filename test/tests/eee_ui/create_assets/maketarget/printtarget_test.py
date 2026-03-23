"""Tests for the MakeTarget PrintTarget operator."""

import bpy
from .... import dynamic_import, ObjectService, TargetService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_PrintTargetOperator = dynamic_import("mpfb.ui.create_assets.maketarget.operators", "MPFB_OT_PrintTargetOperator")


def test_print_target_is_registered():
    assert bpy.ops.mpfb.print_maketarget_target is not None
    assert MPFB_OT_PrintTargetOperator is not None


def test_print_target_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_PrintTargetOperator.poll(bpy.context)


def test_print_target_poll_false_without_primary_target():
    with HumanFixture() as fixture:
        assert not MPFB_OT_PrintTargetOperator.poll(bpy.context)


def test_print_target_poll_true_with_primary_target():
    with HumanFixture() as fixture:
        TargetService.create_shape_key(fixture.basemesh, "PrimaryTarget")
        assert MPFB_OT_PrintTargetOperator.poll(bpy.context)


def test_print_target_execute_successfully():
    with HumanFixture() as fixture:
        TargetService.create_shape_key(fixture.basemesh, "PrimaryTarget")
        mockself = MockOperatorBase()
        result = MPFB_OT_PrintTargetOperator.execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
