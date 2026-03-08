"""Tests for the MakeSkin panel and scene-property registration."""

import bpy
from .... import dynamic_import

MAKESKIN_PROPERTIES = dynamic_import("mpfb.ui.create_assets.makeskin.makeskinpanel", "MAKESKIN_PROPERTIES")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_MakeSkin_Panel')


def test_scene_properties_are_registered():
    assert MAKESKIN_PROPERTIES is not None
    assert hasattr(bpy.types.Scene, 'MPFB_MS_create_diffuse')
    assert hasattr(bpy.types.Scene, 'MPFB_MS_create_roughnessmap')
    assert hasattr(bpy.types.Scene, 'MPFB_MS_resolution')
