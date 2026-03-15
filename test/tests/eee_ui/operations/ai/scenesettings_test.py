"""Tests for the AI OpenPose Scene Settings operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, OpenPoseRigFixture

MPFB_OT_OpenPose_Scene_Settings_Operator = dynamic_import(
    "mpfb.ui.operations.ai.operators.scenesettings",
    "MPFB_OT_OpenPose_Scene_Settings_Operator"
)
AI_PROPERTIES = dynamic_import("mpfb.ui.operations.ai.aipanel", "AI_PROPERTIES")


def test_openpose_scene_settings_is_registered():
    assert bpy.ops.mpfb.openpose_scene_settings is not None
    assert MPFB_OT_OpenPose_Scene_Settings_Operator is not None


def test_openpose_scene_settings_poll_false_no_selection():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_OpenPose_Scene_Settings_Operator.poll(bpy.context)


def test_openpose_scene_settings_poll_true_with_openpose_rig():
    with OpenPoseRigFixture() as fixture:
        assert MPFB_OT_OpenPose_Scene_Settings_Operator.poll(bpy.context)


def test_openpose_scene_settings_executes_with_openpose_rig():
    with OpenPoseRigFixture() as fixture:
        # Disable view mode switch — context.area may be None in headless test
        AI_PROPERTIES.set_value("view", False, entity_reference=bpy.context.scene)
        AI_PROPERTIES.set_value("hide", False, entity_reference=bpy.context.scene)
        AI_PROPERTIES.set_value("background", False, entity_reference=bpy.context.scene)
        AI_PROPERTIES.set_value("render", False, entity_reference=bpy.context.scene)
        mockself = MockOperatorBase()
        result = MPFB_OT_OpenPose_Scene_Settings_Operator.execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
