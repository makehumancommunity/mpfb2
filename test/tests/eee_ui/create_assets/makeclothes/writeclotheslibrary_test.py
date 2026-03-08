"""Tests for the MakeClothes WriteClothesLibrary operator."""

import bpy
from .... import dynamic_import
from ..._helpers import HumanFixture

MPFB_OT_WriteClothesLibraryOperator = dynamic_import("mpfb.ui.create_assets.makeclothes.operators", "MPFB_OT_WriteClothesLibraryOperator")


def test_write_clothes_library_is_registered():
    assert bpy.ops.mpfb.write_makeclothes_library is not None
    assert MPFB_OT_WriteClothesLibraryOperator is not None


def test_write_clothes_library_poll_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_WriteClothesLibraryOperator.poll(bpy.context)
