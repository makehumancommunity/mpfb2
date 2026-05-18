"""Tests for the Standard Rig panel and its scene-property registration."""

import bpy
from .... import dynamic_import

STANDARD_RIG_PROPERTIES = dynamic_import(
    "mpfb.ui.rigging.standardrig.standardrigpanel", "STANDARD_RIG_PROPERTIES"
)
SETUP_HELPERS_PROPERTIES = dynamic_import(
    "mpfb.ui.rigging.standardrig.standardrigpanel", "SETUP_HELPERS_PROPERTIES"
)
MPFB_PT_Standard_Rig_Panel = dynamic_import(
    "mpfb.ui.rigging.standardrig.standardrigpanel", "MPFB_PT_Standard_Rig_Panel"
)


def test_standard_rig_panel_is_registered():
    assert hasattr(bpy.types, "MPFB_PT_Standard_Rig_Panel")
    assert MPFB_PT_Standard_Rig_Panel is not None


def test_standard_rig_properties_not_none():
    assert STANDARD_RIG_PROPERTIES is not None
    assert SETUP_HELPERS_PROPERTIES is not None


def test_standard_rig_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, "MPFB_ADR_standard_rig")
    assert hasattr(bpy.types.Scene, "MPFB_ADR_import_weights")


def test_rig_helpers_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, "MPFB_SIK_arm_helpers_type")
    assert hasattr(bpy.types.Scene, "MPFB_SIK_leg_helpers_type")
    assert hasattr(bpy.types.Scene, "MPFB_SIK_finger_helpers_type")
    assert hasattr(bpy.types.Scene, "MPFB_SIK_eye_ik")
