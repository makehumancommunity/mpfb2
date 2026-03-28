"""Tests for the AnimOps Make Cyclic operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import HumanWithRigFixture

MPFB_OT_Make_Cyclic_Operator = dynamic_import(
    "mpfb.ui.operations.animops.operators.makecyclic",
    "MPFB_OT_Make_Cyclic_Operator"
)


def test_make_cyclic_is_registered():
    assert bpy.ops.mpfb.make_cyclic is not None
    assert MPFB_OT_Make_Cyclic_Operator is not None


def test_make_cyclic_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Make_Cyclic_Operator.poll(bpy.context)


def test_make_cyclic_poll_true_with_rig():
    with HumanWithRigFixture() as fixture:
        assert MPFB_OT_Make_Cyclic_Operator.poll(bpy.context)
