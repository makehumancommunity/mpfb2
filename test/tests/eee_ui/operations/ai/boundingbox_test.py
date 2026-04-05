"""Tests for the AI OpenPose Bounding Box operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Boundingbox_Operator = dynamic_import(
    "mpfb.ui.operations.ai.operators.boundingbox",
    "MPFB_OT_Boundingbox_Operator"
)


def test_boundingbox_is_registered():
    assert bpy.ops.mpfb.boundingbox is not None
    assert MPFB_OT_Boundingbox_Operator is not None


def test_boundingbox_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Boundingbox_Operator.poll(bpy.context)


def test_boundingbox_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Boundingbox_Operator.poll(bpy.context)


def test_boundingbox_executes_with_basemesh():
    with HumanFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_Boundingbox_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
