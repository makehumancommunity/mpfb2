"""Tests for the Sculpt panel and scene-property registration."""

import bpy
from .... import dynamic_import

SCULPT_PROPERTIES = dynamic_import("mpfb.ui.operations.sculpt.sculptpanel", "SCULPT_PROPERTIES")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_SculptPanel')


def test_properties_not_none():
    assert SCULPT_PROPERTIES is not None


def test_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, 'MPFB_SCL_sculpt_strategy')
    assert hasattr(bpy.types.Scene, 'MPFB_SCL_setup_multires')
