"""Tests for the PoseOps panel and scene-property registration."""

import bpy
from .... import dynamic_import

POP_PROPERTIES = dynamic_import("mpfb.ui.operations.poseops.poseopspanel", "POP_PROPERTIES")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_PoseopsPanel')


def test_properties_not_none():
    assert POP_PROPERTIES is not None


def test_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, 'MPFB_POP_only_rotation')
