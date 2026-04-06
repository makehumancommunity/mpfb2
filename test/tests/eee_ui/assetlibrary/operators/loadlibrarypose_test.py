"""Tests for MPFB_OT_Load_Library_Pose_Operator."""

import bpy
from .... import ObjectService, dynamic_import
from ..._helpers import MockOperatorBase, HumanFixture, OpenPoseRigFixture

MPFB_OT_Load_Library_Pose_Operator = dynamic_import(
    "mpfb.ui.assetlibrary.operators.loadlibrarypose",
    "MPFB_OT_Load_Library_Pose_Operator"
)


def test_operator_is_registered():
    assert bpy.ops.mpfb.load_library_pose is not None
    assert MPFB_OT_Load_Library_Pose_Operator is not None


def test_errors_when_active_object_is_not_armature():
    """When the active object is a basemesh (not an armature), loading a pose should fail."""
    with HumanFixture() as fixture:
        # basemesh is active — not an armature and has no skeleton relative
        mockself = MockOperatorBase(filepath="dummy.bvh")
        result = MPFB_OT_Load_Library_Pose_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'CANCELLED'}
        mockself.mock_report.assert_reported('ERROR', 'not an armature')


def test_errors_when_rig_is_not_default_rig():
    """OpenPose rig is a skeleton but not the 'default' rig type — BVH poses require default."""
    with OpenPoseRigFixture() as fixture:
        mockself = MockOperatorBase(filepath="dummy.bvh")
        result = MPFB_OT_Load_Library_Pose_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'CANCELLED'}
        mockself.mock_report.assert_reported('ERROR', 'default rig')
