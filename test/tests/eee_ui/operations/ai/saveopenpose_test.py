"""Tests for the AI OpenPose Save OpenPose operator."""

import bpy
import json
import os
import tempfile
from pytest import approx
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, OpenPoseRigFixture, HumanWithRigFixture, SceneWithCameraFixture

MPFB_OT_Save_Openpose_Operator = dynamic_import(
    "mpfb.ui.operations.ai.operators.saveopenpose",
    "MPFB_OT_Save_Openpose_Operator"
)
AI_PROPERTIES = dynamic_import("mpfb.ui.operations.ai.aipanel", "AI_PROPERTIES")


def test_save_openpose_is_registered():
    assert bpy.ops.mpfb.save_openpose is not None
    assert MPFB_OT_Save_Openpose_Operator is not None


def test_save_openpose_poll_false_no_selected_armature():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Save_Openpose_Operator.poll(bpy.context)


def test_save_openpose_poll_true_with_openpose_rig():
    with OpenPoseRigFixture() as fixture:
        assert MPFB_OT_Save_Openpose_Operator.poll(bpy.context)


def test_save_openpose_executes_with_default_rig_and_camera():
    with HumanWithRigFixture() as fixture:
        with SceneWithCameraFixture() as cam_fixture:
            # Ensure only the armature is selected
            ObjectService.deselect_and_deactivate_all()
            fixture.rig.select_set(True)
            ObjectService.activate_blender_object(fixture.rig)
            tmp_path = os.path.join(tempfile.gettempdir(), "test_openpose.json")
            # Invoke via bpy.ops (ExportHelper operator with instance methods on self)
            result = bpy.ops.mpfb.save_openpose('EXEC_DEFAULT', filepath=tmp_path)
            assert result == {'FINISHED'}


def test_save_openpose_xz_keypoints_are_at_the_joints():
    """In XZ mode the right elbow is at lowerarm01.R's head and the right thumb tip at finger1-3.R's tail."""
    with HumanWithRigFixture() as fixture:
        with SceneWithCameraFixture() as cam_fixture:
            rig = fixture.rig
            scene = bpy.context.scene
            ObjectService.deselect_and_deactivate_all()
            rig.select_set(True)
            ObjectService.activate_blender_object(rig)
            bounds = {"minx": -1.0, "maxx": 1.0, "minz": 0.0, "maxz": 2.0, "resx": 512, "resy": 512}
            for key, value in bounds.items():
                AI_PROPERTIES.set_value(key, value, entity_reference=scene)
            AI_PROPERTIES.set_value("mode", "XZ", entity_reference=scene)
            AI_PROPERTIES.set_value("hands", True, entity_reference=scene)

            tmp_path = os.path.join(tempfile.gettempdir(), "test_openpose_xz.json")
            result = bpy.ops.mpfb.save_openpose('EXEC_DEFAULT', filepath=tmp_path)
            assert result == {'FINISHED'}
            with open(tmp_path) as json_file:
                person = json.load(json_file)["people"][0]

            def projected(point):
                return (512 * (point[0] + 1.0) / 2.0, 512 * (1.0 - point[2] / 2.0))

            elbow = projected(rig.matrix_world @ rig.pose.bones["lowerarm01.R"].head)
            thumb_tip = projected(rig.matrix_world @ rig.pose.bones["finger1-3.R"].tail)
            body = person["pose_keypoints_2d"]
            hand = person["hand_right_keypoints_2d"]
            # COCO point 3 is the right elbow; hand point 4 is the thumb tip
            assert body[9:11] == approx(list(elbow), abs=1e-3)
            assert hand[12:14] == approx(list(thumb_tip), abs=1e-3)
