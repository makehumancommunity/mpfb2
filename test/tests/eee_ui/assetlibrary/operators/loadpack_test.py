"""Tests for MPFB_OT_Load_Pack_Operator."""

import bpy
from .... import dynamic_import

MPFB_OT_Load_Pack_Operator = dynamic_import(
    "mpfb.ui.assetlibrary.operators.loadpack",
    "MPFB_OT_Load_Pack_Operator"
)


def test_operator_is_registered():
    assert bpy.ops.mpfb.load_pack is not None
    assert MPFB_OT_Load_Pack_Operator is not None
