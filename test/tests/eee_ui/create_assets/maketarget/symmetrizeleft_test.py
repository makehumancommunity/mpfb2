"""Tests for the MakeTarget SymmetrizeLeft operator."""

import bpy
from .... import dynamic_import, ObjectService, TargetService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_SymmetrizeLeftOperator = dynamic_import("mpfb.ui.create_assets.maketarget.operators", "MPFB_OT_SymmetrizeLeftOperator")


def test_symmetrize_left_is_registered():
    assert bpy.ops.mpfb.symmetrize_maketarget_left is not None
    assert MPFB_OT_SymmetrizeLeftOperator is not None


def test_symmetrize_left_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_SymmetrizeLeftOperator.poll(bpy.context)


def test_symmetrize_left_poll_false_without_primary_target():
    with HumanFixture() as fixture:
        assert not MPFB_OT_SymmetrizeLeftOperator.poll(bpy.context)


def test_symmetrize_left_poll_true_with_primary_target():
    with HumanFixture() as fixture:
        TargetService.create_shape_key(fixture.basemesh, "PrimaryTarget")
        assert MPFB_OT_SymmetrizeLeftOperator.poll(bpy.context)


def test_symmetrize_left_execute_successfully():
    with HumanFixture() as fixture:
        TargetService.create_shape_key(fixture.basemesh, "PrimaryTarget")
        mockself = MockOperatorBase()
        result = MPFB_OT_SymmetrizeLeftOperator.execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
