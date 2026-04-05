"""Tests for the MakePose SavePose operator."""

import bpy
import os
from .... import dynamic_import, ObjectService, LocationService
from ..._helpers import MockOperatorBase, HumanWithRigFixture

MPFB_OT_Save_Pose_Operator = dynamic_import("mpfb.ui.create_assets.makepose.operators.savepose", "MPFB_OT_Save_Pose_Operator")
MakePoseProperties = dynamic_import("mpfb.ui.create_assets.makepose", "MakePoseProperties")


def test_save_pose_is_registered():
    assert bpy.ops.mpfb.save_pose is not None
    assert MPFB_OT_Save_Pose_Operator is not None


def test_save_pose_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Save_Pose_Operator.poll(bpy.context)


def test_save_pose_poll_true_with_armature():
    with HumanWithRigFixture() as fixture:
        assert MPFB_OT_Save_Pose_Operator.poll(bpy.context)


def test_save_pose_errors_without_name():
    with HumanWithRigFixture() as fixture:
        MakePoseProperties.set_value("name", "", entity_reference=bpy.context.scene)
        mockself = MockOperatorBase()
        result = MPFB_OT_Save_Pose_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_reported('ERROR', "valid name")


def test_save_pose_executes_successfully():
    created_path = None
    try:
        with HumanWithRigFixture() as fixture:
            scene = bpy.context.scene
            MakePoseProperties.set_value("name", "test_pose", entity_reference=scene)
            MakePoseProperties.set_value("pose_type", "AUTO", entity_reference=scene)
            MakePoseProperties.set_value("overwrite", True, entity_reference=scene)
            mockself = MockOperatorBase()
            result = MPFB_OT_Save_Pose_Operator.hardened_execute(mockself, bpy.context)
            assert result == {'FINISHED'}
            mockself.mock_report.assert_no_errors()
            # Find the created file
            poses_root = LocationService.get_user_data("poses")
            for dirpath, dirnames, filenames in os.walk(poses_root):
                for fname in filenames:
                    if fname == "test_pose.json":
                        created_path = os.path.join(dirpath, fname)
                        break
    finally:
        if created_path and os.path.exists(created_path):
            os.remove(created_path)
