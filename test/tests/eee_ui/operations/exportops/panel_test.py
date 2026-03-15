"""Tests for the ExportOps panel and scene-property registration."""

import bpy
from .... import dynamic_import

EXPORTOPS_PROPERTIES = dynamic_import("mpfb.ui.operations.exportops.exportopspanel", "EXPORTOPS_PROPERTIES")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_ExportOpsPanel')


def test_properties_not_none():
    assert EXPORTOPS_PROPERTIES is not None


def test_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, 'MPFB_EXPO_bake_shapekeys')
    assert hasattr(bpy.types.Scene, 'MPFB_EXPO_suffix')
