"""Tests for the Rigify Rig panel and its scene-property registration."""

import bpy
from .... import dynamic_import

RIGIFY_RIG_PROPERTIES = dynamic_import(
    "mpfb.ui.rigging.rigifyrig.rigifyrigpanel", "RIGIFY_RIG_PROPERTIES"
)
MPFB_PT_Rigify_Rig_Panel = dynamic_import(
    "mpfb.ui.rigging.rigifyrig.rigifyrigpanel", "MPFB_PT_Rigify_Rig_Panel"
)


def test_rigify_rig_panel_is_registered():
    assert hasattr(bpy.types, "MPFB_PT_Rigify_Rig_Panel")
    assert MPFB_PT_Rigify_Rig_Panel is not None


def test_rigify_rig_properties_not_none():
    assert RIGIFY_RIG_PROPERTIES is not None


def test_rigify_rig_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, "MPFB_ADR_rigify_rig")
    assert hasattr(bpy.types.Scene, "MPFB_ADR_import_weights_rigify")
    assert hasattr(bpy.types.Scene, "MPFB_ADR_name")
    assert hasattr(bpy.types.Scene, "MPFB_ADR_auto_generate")
    assert hasattr(bpy.types.Scene, "MPFB_ADR_meta_rig_action")
