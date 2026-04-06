"""Tests for the PoseOps Copy Pose operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanWithRigFixture, TwoHumansWithRigsFixture

MPFB_OT_Copy_Pose_Operator = dynamic_import(
    "mpfb.ui.operations.poseops.operators.copy_pose",
    "MPFB_OT_Copy_Pose_Operator"
)


def test_copy_pose_is_registered():
    assert bpy.ops.mpfb.copy_pose is not None
    assert MPFB_OT_Copy_Pose_Operator is not None


def test_copy_pose_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Copy_Pose_Operator.poll(bpy.context)


def test_copy_pose_poll_true_with_rig():
    with HumanWithRigFixture() as fixture:
        assert MPFB_OT_Copy_Pose_Operator.poll(bpy.context)


def test_copy_pose_executes_with_two_rigs():
    with TwoHumansWithRigsFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_Copy_Pose_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
