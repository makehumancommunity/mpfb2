"""Tests for the MakeSkin WriteLibrary operator."""

import bpy
from .... import ObjectService, dynamic_import
from ..._helpers import HumanFixture

MPFB_OT_WriteLibraryOperator = dynamic_import("mpfb.ui.create_assets.makeskin.operators", "MPFB_OT_WriteLibraryOperator")


def test_write_library_is_registered():
    assert bpy.ops.mpfb.write_makeskin_to_library is not None
    assert MPFB_OT_WriteLibraryOperator is not None


def test_write_library_poll_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_WriteLibraryOperator.poll(bpy.context)
