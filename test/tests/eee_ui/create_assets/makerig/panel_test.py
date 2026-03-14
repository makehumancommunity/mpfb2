"""Tests for the MakeRig panel and scene-property registration."""

import bpy
from .... import dynamic_import

MakeRigProperties = dynamic_import("mpfb.ui.create_assets.makerig", "MakeRigProperties")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_MakeRig_Panel')


def test_scene_properties_are_registered():
    assert MakeRigProperties is not None
