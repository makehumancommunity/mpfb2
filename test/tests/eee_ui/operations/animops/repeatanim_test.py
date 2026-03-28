"""Tests for the AnimOps Repeat Animation operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import HumanWithRigFixture

MPFB_OT_Repeat_Animation_Operator = dynamic_import(
    "mpfb.ui.operations.animops.operators.repeatanim",
    "MPFB_OT_Repeat_Animation_Operator"
)


def test_repeat_animation_is_registered():
    assert bpy.ops.mpfb.repeat_animation is not None
    assert MPFB_OT_Repeat_Animation_Operator is not None


def test_repeat_animation_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Repeat_Animation_Operator.poll(bpy.context)


def test_repeat_animation_poll_true_with_rig():
    with HumanWithRigFixture() as fixture:
        assert MPFB_OT_Repeat_Animation_Operator.poll(bpy.context)
