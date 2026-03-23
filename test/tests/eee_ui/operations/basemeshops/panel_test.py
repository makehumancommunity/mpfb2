"""Tests for the BasemeshOps panel registration."""

import bpy
from .... import dynamic_import


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_BasemeshOpsPanel')
