"""Tests for the MakeClothes GenDelete operator."""

import bpy
from .... import dynamic_import
from ..._helpers import HumanFixture

MPFB_OT_GenDeleteOperator = dynamic_import("mpfb.ui.create_assets.makeclothes.operators", "MPFB_OT_GenDeleteOperator")


def test_gendelete_is_registered():
    assert bpy.ops.mpfb.makeclothes_gendelete is not None
    assert MPFB_OT_GenDeleteOperator is not None


def test_gendelete_poll_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_GenDeleteOperator.poll(bpy.context)
