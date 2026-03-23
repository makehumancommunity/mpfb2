"""Tests for the Convert to Rigify operator.

The execute test uses the default rig (not the game-engine skeleton), so the operator
reports an error about unsupported skeleton type — this is the expected, safe path.
"""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanWithRigFixture

MPFB_OT_Convert_To_Rigify_Operator = dynamic_import(
    "mpfb.ui.rigging.rigify.operators.converttorigify",
    "MPFB_OT_Convert_To_Rigify_Operator",
)


def test_convert_to_rigify_is_registered():
    assert bpy.ops.mpfb.convert_to_rigify is not None
    assert MPFB_OT_Convert_To_Rigify_Operator is not None


def test_convert_to_rigify_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Convert_To_Rigify_Operator.poll(bpy.context)


def test_convert_to_rigify_poll_true_with_rig():
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        assert MPFB_OT_Convert_To_Rigify_Operator.poll(bpy.context)


def test_convert_to_rigify_executes_with_default_rig():
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        mockself = MockOperatorBase()
        result = MPFB_OT_Convert_To_Rigify_Operator.execute(mockself, bpy.context)
        assert result == {"FINISHED"}
        # Default rig does not have a "ball_r" bone; operator reports an error about
        # unsupported skeleton type — this is the expected graceful-failure path
        mockself.mock_report.assert_reported("ERROR", "Game engine")
