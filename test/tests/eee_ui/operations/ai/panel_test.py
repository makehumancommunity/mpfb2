"""Tests for the AI (OpenPose) panel and scene-property registration."""

import bpy
from .... import dynamic_import

AI_PROPERTIES = dynamic_import("mpfb.ui.operations.ai.aipanel", "AI_PROPERTIES")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_Ai_Panel')


def test_properties_not_none():
    assert AI_PROPERTIES is not None


def test_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, 'MPFB_AI_mode')
    assert hasattr(bpy.types.Scene, 'MPFB_AI_bone_size')
    assert hasattr(bpy.types.Scene, 'MPFB_AI_hands')
