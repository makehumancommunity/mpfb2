"""Tests for the MakeTarget panel and object-property registration."""

import bpy
from .... import dynamic_import

MPFB_PT_MakeTarget_Panel = dynamic_import("mpfb.ui.create_assets.maketarget", "MPFB_PT_MakeTarget_Panel")
MakeTargetObjectProperties = dynamic_import("mpfb.ui.create_assets.maketarget", "MakeTargetObjectProperties")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_MakeTarget_Panel')


def test_object_properties_are_registered():
    assert MakeTargetObjectProperties is not None
    assert hasattr(bpy.types.Object, 'MPFB_MT_name')
