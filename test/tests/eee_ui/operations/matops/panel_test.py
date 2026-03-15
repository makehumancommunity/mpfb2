"""Tests for the MatOps panel and scene-property registration."""

import bpy
from .... import dynamic_import

MATOPS_PROPERTIES = dynamic_import("mpfb.ui.operations.matops.matopspanel", "MATOPS_PROPERTIES")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_MatopsPanel')


def test_properties_not_none():
    assert MATOPS_PROPERTIES is not None


def test_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, 'MPFB_MATO_recreate_groups')
    assert hasattr(bpy.types.Scene, 'MPFB_MATO_reuse_textures')
