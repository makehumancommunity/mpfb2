"""Tests for the MatOps Remove Makeup operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, BasemeshWithV2SkinFixture

MPFB_OT_Remove_Makeup_Operator = dynamic_import(
    "mpfb.ui.operations.matops.operators.removemakeup",
    "MPFB_OT_Remove_Makeup_Operator"
)


def test_remove_makeup_is_registered():
    assert bpy.ops.mpfb.remove_makeup is not None
    assert MPFB_OT_Remove_Makeup_Operator is not None


def test_remove_makeup_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Remove_Makeup_Operator.poll(bpy.context)


def test_remove_makeup_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Remove_Makeup_Operator.poll(bpy.context)


def test_remove_makeup_executes_with_v2_skin():
    with BasemeshWithV2SkinFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_Remove_Makeup_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
