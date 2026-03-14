"""Tests for the MakePose panel and scene-property registration."""

import bpy
from .... import dynamic_import

MakePoseProperties = dynamic_import("mpfb.ui.create_assets.makepose", "MakePoseProperties")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_MakePose_Panel')


def test_scene_properties_are_registered():
    assert MakePoseProperties is not None
