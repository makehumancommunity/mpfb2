"""Tests for the MakeClothes panel and scene-property registration."""

import bpy
from .... import dynamic_import

MAKECLOTHES_PROPERTIES = dynamic_import("mpfb.ui.create_assets.makeclothes.makeclothespanel", "MAKECLOTHES_PROPERTIES")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_MakeClothes_Panel')


def test_scene_properties_are_registered():
    assert MAKECLOTHES_PROPERTIES is not None
