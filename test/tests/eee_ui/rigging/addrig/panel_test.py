"""Tests for the Add Rig panel and its scene-property registration."""

import bpy
from .... import dynamic_import

ADD_RIG_PROPERTIES = dynamic_import(
    "mpfb.ui.rigging.addrig.addrigpanel", "ADD_RIG_PROPERTIES"
)
MPFB_PT_Add_Rig_Panel = dynamic_import(
    "mpfb.ui.rigging.addrig.addrigpanel", "MPFB_PT_Add_Rig_Panel"
)


def test_add_rig_panel_is_registered():
    assert hasattr(bpy.types, "MPFB_PT_Add_Rig_Panel")
    assert MPFB_PT_Add_Rig_Panel is not None


def test_add_rig_properties_not_none():
    assert ADD_RIG_PROPERTIES is not None


def test_add_rig_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, "MPFB_ADR_standard_rig")
    assert hasattr(bpy.types.Scene, "MPFB_ADR_import_weights")
    assert hasattr(bpy.types.Scene, "MPFB_ADR_rigify_rig")
    assert hasattr(bpy.types.Scene, "MPFB_ADR_import_weights_rigify")
    assert hasattr(bpy.types.Scene, "MPFB_ADR_delete_after_generate")
    assert hasattr(bpy.types.Scene, "MPFB_ADR_name")
    assert hasattr(bpy.types.Scene, "MPFB_ADR_custom_rig")
    assert hasattr(bpy.types.Scene, "MPFB_ADR_import_weights_custom")
