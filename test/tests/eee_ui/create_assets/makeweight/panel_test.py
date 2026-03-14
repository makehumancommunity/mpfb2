"""Tests for the MakeWeight panel and scene-property registration."""

import bpy
from .... import dynamic_import

MAKEWEIGHT_PROPERTIES = dynamic_import("mpfb.ui.create_assets.makeweight.makeweightpanel", "MAKEWEIGHT_PROPERTIES")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_MakeWeight_Panel')


def test_scene_properties_are_registered():
    assert MAKEWEIGHT_PROPERTIES is not None
