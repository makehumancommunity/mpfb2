"""Tests for the Developer LoadTarget operator."""

import bpy
from ... import dynamic_import, ObjectService
from .._helpers import HumanFixture

MPFB_OT_Load_Target_Operator = dynamic_import(
    "mpfb.ui.developer.operators.loadtarget",
    "MPFB_OT_Load_Target_Operator"
)


def test_load_target_is_registered():
    assert bpy.ops.mpfb.load_target is not None
    assert MPFB_OT_Load_Target_Operator is not None


def test_load_target_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Load_Target_Operator.poll(bpy.context)


def test_load_target_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Load_Target_Operator.poll(bpy.context)
