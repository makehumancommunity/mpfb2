"""Tests for the AnimOps Reduced Doll operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, HumanWithRigFixture

MPFB_OT_Reduced_Doll_Operator = dynamic_import(
    "mpfb.ui.operations.animops.operators.reduceddoll",
    "MPFB_OT_Reduced_Doll_Operator"
)


def test_reduced_doll_is_registered():
    assert bpy.ops.mpfb.reduced_doll is not None
    assert MPFB_OT_Reduced_Doll_Operator is not None


def test_reduced_doll_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Reduced_Doll_Operator.poll(bpy.context)


def test_reduced_doll_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Reduced_Doll_Operator.poll(bpy.context)


# TODO: Better test for actual functionality

