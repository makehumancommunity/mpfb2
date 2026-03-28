"""Tests for the MakeClothes BasemeshXref operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import HumanFixture

MPFB_OT_BasemeshXrefOperator = dynamic_import("mpfb.ui.create_assets.makeclothes.operators", "MPFB_OT_BasemeshXrefOperator")


def test_basemesh_xref_is_registered():
    assert bpy.ops.mpfb.basemesh_xref is not None
    assert MPFB_OT_BasemeshXrefOperator is not None


def test_basemesh_xref_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_BasemeshXrefOperator.poll(bpy.context)


def test_basemesh_xref_poll_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_BasemeshXrefOperator.poll(bpy.context)
