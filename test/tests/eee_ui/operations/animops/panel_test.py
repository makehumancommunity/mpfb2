"""Tests for the AnimOps panel and scene-property registration."""

import bpy
from .... import dynamic_import

ANIMOPS_PROPERTIES = dynamic_import("mpfb.ui.operations.animops.animopspanel", "ANIMOPS_PROPERTIES")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_AnimopsPanel')


def test_properties_not_none():
    assert ANIMOPS_PROPERTIES is not None


def test_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, 'MPFB_ANIO_call_fbx')
    assert hasattr(bpy.types.Scene, 'MPFB_ANIO_shiftroot')
    assert hasattr(bpy.types.Scene, 'MPFB_ANIO_iterations')
