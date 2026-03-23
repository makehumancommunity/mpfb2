"""Tests for the Rig Helpers panel and its scene-property registration."""

import bpy
from .... import dynamic_import

SETUP_HELPERS_PROPERTIES = dynamic_import(
    "mpfb.ui.rigging.righelpers.righelperspanel", "SETUP_HELPERS_PROPERTIES"
)
MPFB_PT_RigHelpersPanel = dynamic_import(
    "mpfb.ui.rigging.righelpers.righelperspanel", "MPFB_PT_RigHelpersPanel"
)


def test_rig_helpers_panel_is_registered():
    assert hasattr(bpy.types, "MPFB_PT_RigHelpersPanel")
    assert MPFB_PT_RigHelpersPanel is not None


def test_setup_helpers_properties_not_none():
    assert SETUP_HELPERS_PROPERTIES is not None


def test_rig_helpers_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, "MPFB_SIK_arm_helpers_type")
    assert hasattr(bpy.types.Scene, "MPFB_SIK_leg_helpers_type")
    assert hasattr(bpy.types.Scene, "MPFB_SIK_finger_helpers_type")
    assert hasattr(bpy.types.Scene, "MPFB_SIK_eye_ik")
