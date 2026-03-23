"""Tests for the Add Cycle Load Walk Cycle operator.

Note: the addcycle panel is deprecated and ADD_CYCLE_PROPERTIES is not defined in
addcyclepanel.py, so execute() cannot be safely called without hitting an ImportError.
Registration and poll tests are provided; the execute test is omitted.
"""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanWithRigFixture

MPFB_OT_Load_Walk_Cycle_Operator = dynamic_import(
    "mpfb.ui.rigging.addcycle.operators.loadcycle", "MPFB_OT_Load_Walk_Cycle_Operator"
)


def test_load_walk_cycle_is_registered():
    assert bpy.ops.mpfb.load_walk_cycle is not None
    assert MPFB_OT_Load_Walk_Cycle_Operator is not None


def test_load_walk_cycle_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Load_Walk_Cycle_Operator.poll(bpy.context)


def test_load_walk_cycle_poll_true_with_rig():
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        assert MPFB_OT_Load_Walk_Cycle_Operator.poll(bpy.context)
