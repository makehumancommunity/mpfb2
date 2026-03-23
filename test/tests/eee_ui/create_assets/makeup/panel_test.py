"""Tests for the MakeUp panel and scene-property registration."""

import bpy
from .... import dynamic_import

MAKEUP_PROPERTIES = dynamic_import("mpfb.ui.create_assets.makeup.makeuppanel", "MAKEUP_PROPERTIES")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_MakeUp_Panel')


def test_scene_properties_are_registered():
    assert MAKEUP_PROPERTIES is not None
    assert hasattr(bpy.types.Scene, 'MPFB_MAKU_uv_map_name')
