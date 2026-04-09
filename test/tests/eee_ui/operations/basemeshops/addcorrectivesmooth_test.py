"""Tests for the BasemeshOps Add Corrective Smooth operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Add_Corrective_Smooth_Operator = dynamic_import(
    "mpfb.ui.operations.basemeshops.operators.addcorrectivesmooth",
    "MPFB_OT_Add_Corrective_Smooth_Operator"
)


def test_add_corrective_smooth_is_registered():
    assert bpy.ops.mpfb.add_corrective_smooth is not None
    assert MPFB_OT_Add_Corrective_Smooth_Operator is not None


def test_add_corrective_smooth_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Add_Corrective_Smooth_Operator.poll(bpy.context)


def test_add_corrective_smooth_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Add_Corrective_Smooth_Operator.poll(bpy.context)


def test_add_corrective_smooth_executes_with_basemesh():
    with HumanFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_Add_Corrective_Smooth_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
