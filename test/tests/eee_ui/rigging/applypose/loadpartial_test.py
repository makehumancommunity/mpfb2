"""Tests for the Apply Pose Load Partial operator.

When no partial pose name is selected (the default), execute reports an error.
"""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanWithRigFixture

MPFB_OT_Load_Partial_Operator = dynamic_import(
    "mpfb.ui.rigging.applypose.operators.loadpartial", "MPFB_OT_Load_Partial_Operator"
)


def test_load_partial_is_registered():
    assert bpy.ops.mpfb.load_partial is not None
    assert MPFB_OT_Load_Partial_Operator is not None


def test_load_partial_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Load_Partial_Operator.poll(bpy.context)


def test_load_partial_poll_true_with_rig():
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        assert MPFB_OT_Load_Partial_Operator.poll(bpy.context)


def test_load_partial_executes_reports_error_no_pose_selected():
    with HumanWithRigFixture() as fixture:
        bpy.context.view_layer.objects.active = fixture.rig
        mockself = MockOperatorBase()
        result = MPFB_OT_Load_Partial_Operator.execute(mockself, bpy.context)
        assert result == {"FINISHED"}
        # No partial pose is selected by default; expect an error report
        mockself.mock_report.assert_reported("ERROR", "Must select a valid pose name")
