"""Tests for the Add Rig Add Rigify Rig operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_AddRigifyRigOperator = dynamic_import(
    "mpfb.ui.rigging.addrig.operators.addrigifyrig", "MPFB_OT_AddRigifyRigOperator"
)


def test_add_rigify_rig_is_registered():
    assert bpy.ops.mpfb.add_rigify_rig is not None
    assert MPFB_OT_AddRigifyRigOperator is not None


def test_add_rigify_rig_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_AddRigifyRigOperator.poll(bpy.context)


def test_add_rigify_rig_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_AddRigifyRigOperator.poll(bpy.context)


def test_add_rigify_rig_executes_with_basemesh():
    with HumanFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_AddRigifyRigOperator.execute(mockself, bpy.context)
        assert result == {"FINISHED"}
        mockself.mock_report.assert_no_errors()
