"""Tests for the MakeClothes WriteClothes operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import HumanFixture

MPFB_OT_WriteClothesOperator = dynamic_import("mpfb.ui.create_assets.makeclothes.operators", "MPFB_OT_WriteClothesOperator")


def test_write_clothes_is_registered():
    assert bpy.ops.mpfb.write_makeclothes_clothes is not None
    assert MPFB_OT_WriteClothesOperator is not None


def test_write_clothes_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_WriteClothesOperator.poll(bpy.context)


def test_write_clothes_poll_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_WriteClothesOperator.poll(bpy.context)
