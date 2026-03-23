"""Tests for the Add Rig Add Custom Rig operator.

When no custom rig is selected (the default), execute reports an error.
"""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Add_Custom_Rig_Operator = dynamic_import(
    "mpfb.ui.rigging.addrig.operators.addcustomrig", "MPFB_OT_Add_Custom_Rig_Operator"
)


def test_add_custom_rig_is_registered():
    assert bpy.ops.mpfb.add_custom_rig is not None
    assert MPFB_OT_Add_Custom_Rig_Operator is not None


def test_add_custom_rig_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Add_Custom_Rig_Operator.poll(bpy.context)


def test_add_custom_rig_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Add_Custom_Rig_Operator.poll(bpy.context)


def test_add_custom_rig_executes_reports_error_no_rig_selected():
    with HumanFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_Add_Custom_Rig_Operator.execute(mockself, bpy.context)
        assert result == {"FINISHED"}
        # No custom rig is selected by default; expect an error report
        mockself.mock_report.assert_reported("ERROR", "No custom rig selected")
