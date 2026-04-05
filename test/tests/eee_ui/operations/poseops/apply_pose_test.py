"""Tests for the PoseOps Apply Pose operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, HumanWithRigFixture

MPFB_OT_Apply_Pose_Operator = dynamic_import(
    "mpfb.ui.operations.poseops.operators.apply_pose",
    "MPFB_OT_Apply_Pose_Operator"
)


def test_apply_pose_is_registered():
    assert bpy.ops.mpfb.apply_pose is not None
    assert MPFB_OT_Apply_Pose_Operator is not None


def test_apply_pose_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Apply_Pose_Operator.poll(bpy.context)


def test_apply_pose_poll_false_with_basemesh():
    with HumanFixture() as fixture:
        assert not MPFB_OT_Apply_Pose_Operator.poll(bpy.context)


def test_apply_pose_poll_true_with_rig():
    with HumanWithRigFixture() as fixture:
        assert MPFB_OT_Apply_Pose_Operator.poll(bpy.context)


def test_apply_pose_executes_with_rig():
    with HumanWithRigFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_Apply_Pose_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
