"""Tests for the Add Rig Add Standard Rig operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_AddStandardRigOperator = dynamic_import(
    "mpfb.ui.rigging.addrig.operators.addstandardrig", "MPFB_OT_AddStandardRigOperator"
)


def test_add_standard_rig_is_registered():
    assert bpy.ops.mpfb.add_standard_rig is not None
    assert MPFB_OT_AddStandardRigOperator is not None


def test_add_standard_rig_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_AddStandardRigOperator.poll(bpy.context)


def test_add_standard_rig_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_AddStandardRigOperator.poll(bpy.context)


def test_add_standard_rig_executes_with_basemesh():
    with HumanFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_AddStandardRigOperator.hardened_execute(mockself, bpy.context)
        assert result == {"FINISHED"}
        mockself.mock_report.assert_no_errors()
