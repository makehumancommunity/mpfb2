"""Tests for the Rig Helpers Add Helpers operator.

The operator uses internal instance methods (_arm_helpers, _leg_helpers, etc.) that
require a real operator instance. The execute test therefore calls bpy.ops directly.
"""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import HumanWithRigFixture

MPFB_OT_AddHelpersOperator = dynamic_import(
    "mpfb.ui.rigging.righelpers.operators.addhelpers", "MPFB_OT_AddHelpersOperator"
)


def test_add_helpers_is_registered():
    assert bpy.ops.mpfb.add_helpers is not None
    assert MPFB_OT_AddHelpersOperator is not None


def test_add_helpers_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_AddHelpersOperator.poll(bpy.context)


def test_add_helpers_poll_true_with_rig():
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        assert MPFB_OT_AddHelpersOperator.poll(bpy.context)


def test_add_helpers_executes_with_default_rig():
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        # Operator uses self._arm_helpers() etc. — requires real operator instance via bpy.ops
        result = bpy.ops.mpfb.add_helpers()
        assert result == {"FINISHED"}
