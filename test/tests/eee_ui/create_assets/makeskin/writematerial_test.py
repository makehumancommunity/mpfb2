"""Tests for the MakeSkin WriteMaterial operator."""

import bpy
from .... import dynamic_import

MPFB_OT_WriteMaterialOperator = dynamic_import("mpfb.ui.create_assets.makeskin.operators", "MPFB_OT_WriteMaterialOperator")


def test_write_material_is_registered():
    assert bpy.ops.mpfb.write_makeskin_material is not None
    assert MPFB_OT_WriteMaterialOperator is not None
