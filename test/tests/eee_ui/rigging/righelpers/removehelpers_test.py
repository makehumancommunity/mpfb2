"""Tests for the Rig Helpers Remove Helpers operator.

The poll requires at least one helper mode (arm/leg/finger/eye) to be set on the armature.
We set one via RigHelpersProperties to make poll return True.
"""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanWithRigFixture

MPFB_OT_RemoveHelpersOperator = dynamic_import(
    "mpfb.ui.rigging.righelpers.operators.removehelpers", "MPFB_OT_RemoveHelpersOperator"
)
RigHelpersProperties = dynamic_import(
    "mpfb.ui.rigging.righelpers", "RigHelpersProperties"
)


def test_remove_helpers_is_registered():
    assert bpy.ops.mpfb.remove_helpers is not None
    assert MPFB_OT_RemoveHelpersOperator is not None


def test_remove_helpers_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_RemoveHelpersOperator.poll(bpy.context)


def test_remove_helpers_poll_false_no_helpers_set():
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        # No helpers are set; poll should return False
        assert not MPFB_OT_RemoveHelpersOperator.poll(bpy.context)


def test_remove_helpers_poll_true_with_arm_mode_set():
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        RigHelpersProperties.set_value("arm_mode", "IK", entity_reference=fixture.rig)
        assert MPFB_OT_RemoveHelpersOperator.poll(bpy.context)
        # Clean up
        RigHelpersProperties.set_value("arm_mode", "", entity_reference=fixture.rig)


def test_remove_helpers_executes_with_no_helpers_applied():
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        mockself = MockOperatorBase()
        result = MPFB_OT_RemoveHelpersOperator.hardened_execute(mockself, bpy.context)
        assert result == {"FINISHED"}
        mockself.mock_report.assert_no_errors()
