"""Tests for the Apply Pose panel and its scene-property registration."""

import bpy
from .... import dynamic_import

POSES_PROPERTIES = dynamic_import(
    "mpfb.ui.rigging.applypose.applyposepanel", "POSES_PROPERTIES"
)
MPFB_PT_ApplyPosePanel = dynamic_import(
    "mpfb.ui.rigging.applypose.applyposepanel", "MPFB_PT_ApplyPosePanel"
)


def test_apply_pose_panel_is_registered():
    assert hasattr(bpy.types, "MPFB_PT_ApplyPosePanel")
    assert MPFB_PT_ApplyPosePanel is not None


def test_poses_properties_not_none():
    assert POSES_PROPERTIES is not None


def test_poses_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, "MPFB_POSES_available_poses")
    assert hasattr(bpy.types.Scene, "MPFB_POSES_available_partials")
