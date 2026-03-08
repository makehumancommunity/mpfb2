"""Tests for the MakeClothes ExtractClothes operator."""

import bpy
from .... import ObjectService, dynamic_import
from ..._helpers import HumanFixture

MPFB_OT_ExtractClothesOperator = dynamic_import("mpfb.ui.create_assets.makeclothes.operators", "MPFB_OT_ExtractClothesOperator")


def test_extract_clothes_is_registered():
    assert bpy.ops.mpfb.extract_makeclothes_clothes is not None
    assert MPFB_OT_ExtractClothesOperator is not None


def test_extract_clothes_poll_false_with_no_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_ExtractClothesOperator.poll(bpy.context)


def test_extract_clothes_poll_true_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_ExtractClothesOperator.poll(bpy.context)
