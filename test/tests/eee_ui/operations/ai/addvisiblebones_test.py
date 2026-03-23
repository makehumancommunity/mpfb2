"""Tests for the AI OpenPose Add Visible Bones operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, OpenPoseRigFixture

MPFB_OT_OpenPose_Visible_Bones_Operator = dynamic_import(
    "mpfb.ui.operations.ai.operators.addvisiblebones",
    "MPFB_OT_OpenPose_Visible_Bones_Operator"
)


def test_openpose_visible_bones_is_registered():
    assert bpy.ops.mpfb.openpose_visible_bones is not None
    assert MPFB_OT_OpenPose_Visible_Bones_Operator is not None


def test_openpose_visible_bones_poll_false_no_selected_armature():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_OpenPose_Visible_Bones_Operator.poll(bpy.context)


def test_openpose_visible_bones_poll_true_with_openpose_rig():
    with OpenPoseRigFixture() as fixture:
        assert MPFB_OT_OpenPose_Visible_Bones_Operator.poll(bpy.context)


def test_openpose_visible_bones_executes_with_openpose_rig():
    with OpenPoseRigFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_OpenPose_Visible_Bones_Operator.execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
