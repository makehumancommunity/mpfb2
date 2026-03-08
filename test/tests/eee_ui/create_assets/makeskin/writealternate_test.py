"""Tests for the MakeSkin WriteAlternate operator."""

import bpy
from .... import ObjectService, dynamic_import
from ..._helpers import HumanWithRigAndClothesFixture

MPFB_OT_WriteAlternateOperator = dynamic_import("mpfb.ui.create_assets.makeskin.operators", "MPFB_OT_WriteAlternateOperator")


def test_write_alternate_is_registered():
    assert bpy.ops.mpfb.write_alternate is not None
    assert MPFB_OT_WriteAlternateOperator is not None


def test_write_alternate_poll_false_with_basemesh():
    with HumanWithRigAndClothesFixture() as fixture:
        ObjectService.activate_blender_object(fixture.basemesh)
        assert not MPFB_OT_WriteAlternateOperator.poll(bpy.context)


def test_write_alternate_poll_true_with_clothes():
    with HumanWithRigAndClothesFixture() as fixture:
        ObjectService.activate_blender_object(fixture.clothes)
        assert MPFB_OT_WriteAlternateOperator.poll(bpy.context)
