"""Tests for the FaceOps panel and scene-property registration."""

import bpy
from .... import dynamic_import

FACEOPS_PROPERTIES = dynamic_import("mpfb.ui.operations.faceops.faceopspanel", "FACEOPS_PROPERTIES")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_FaceOpsPanel')


def test_properties_not_none():
    assert FACEOPS_PROPERTIES is not None


def test_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, 'MPFB_FAOP_visemes01')
    assert hasattr(bpy.types.Scene, 'MPFB_FAOP_visemes02')
    assert hasattr(bpy.types.Scene, 'MPFB_FAOP_faceunits01')
