"""Tests for the AI OpenPose Save OpenPose operator."""

import bpy
import os
import tempfile
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, OpenPoseRigFixture, HumanWithRigFixture, SceneWithCameraFixture

MPFB_OT_Save_Openpose_Operator = dynamic_import(
    "mpfb.ui.operations.ai.operators.saveopenpose",
    "MPFB_OT_Save_Openpose_Operator"
)


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
