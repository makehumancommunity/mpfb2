"""Tests for the MakeWeight SymmetrizeRight operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, HumanWithRigFixture

MPFB_OT_SymmetrizeRightOperator = dynamic_import("mpfb.ui.create_assets.makeweight.operators.symmetrizeright", "MPFB_OT_SymmetrizeRightOperator")


def test_symmetrize_right_is_registered():
    assert bpy.ops.mpfb.symmetrize_makeweight_right is not None
    assert MPFB_OT_SymmetrizeRightOperator is not None


def test_symmetrize_right_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_SymmetrizeRightOperator.poll(bpy.context)


def test_symmetrize_right_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_SymmetrizeRightOperator.poll(bpy.context)


def test_symmetrize_right_execute_errors_without_rig():
    with HumanFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_SymmetrizeRightOperator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_reported('ERROR', "Could not find a rig")


def test_symmetrize_right_execute_with_rig():
    with HumanWithRigFixture() as fixture:
        ObjectService.activate_blender_object(fixture.basemesh)
        mockself = MockOperatorBase()
        result = MPFB_OT_SymmetrizeRightOperator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
