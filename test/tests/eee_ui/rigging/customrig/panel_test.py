"""Tests for the Custom Rig panel and its scene-property registration."""

import bpy
from .... import dynamic_import

CUSTOM_RIG_PROPERTIES = dynamic_import(
    "mpfb.ui.rigging.customrig.customrigpanel", "CUSTOM_RIG_PROPERTIES"
)
MPFB_PT_Custom_Rig_Panel = dynamic_import(
    "mpfb.ui.rigging.customrig.customrigpanel", "MPFB_PT_Custom_Rig_Panel"
)


def test_custom_rig_panel_is_registered():
    assert hasattr(bpy.types, "MPFB_PT_Custom_Rig_Panel")
    assert MPFB_PT_Custom_Rig_Panel is not None


def test_custom_rig_properties_not_none():
    assert CUSTOM_RIG_PROPERTIES is not None


def test_custom_rig_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, "MPFB_ADR_custom_rig")
    assert hasattr(bpy.types.Scene, "MPFB_ADR_import_weights_custom")
