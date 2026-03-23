"""Tests for the Convert to Rigify panel and its scene-property registration."""

import bpy
from .... import dynamic_import

RIGIFY_PROPERTIES = dynamic_import(
    "mpfb.ui.rigging.rigify.rigifypanel", "RIGIFY_PROPERTIES"
)
MPFB_PT_Rigify_Panel = dynamic_import(
    "mpfb.ui.rigging.rigify.rigifypanel", "MPFB_PT_Rigify_Panel"
)


def test_rigify_panel_is_registered():
    assert hasattr(bpy.types, "MPFB_PT_Rigify_Panel")
    assert MPFB_PT_Rigify_Panel is not None


def test_rigify_properties_not_none():
    assert RIGIFY_PROPERTIES is not None


def test_rigify_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, "MPFB_RF_name")
    assert hasattr(bpy.types.Scene, "MPFB_RF_produce")
    assert hasattr(bpy.types.Scene, "MPFB_RF_keep_meta")
