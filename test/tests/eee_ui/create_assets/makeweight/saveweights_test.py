"""Tests for the MakeWeight SaveWeights operator."""

import bpy
import tempfile
import os
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, HumanWithRigFixture

MPFB_OT_SaveWeightsOperator = dynamic_import("mpfb.ui.create_assets.makeweight.operators.saveweights", "MPFB_OT_SaveWeightsOperator")


def test_save_makeweight_weight_is_registered():
    assert bpy.ops.mpfb.save_makeweight_weight is not None
    assert MPFB_OT_SaveWeightsOperator is not None


def test_save_makeweight_weight_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_SaveWeightsOperator.poll(bpy.context)


def test_save_makeweight_weight_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_SaveWeightsOperator.poll(bpy.context)


def test_save_makeweight_weight_errors_without_armature():
    with HumanFixture() as fixture:
        # Active object is basemesh, not armature — execute should report ERROR
        mockself = MockOperatorBase(filepath="/tmp/test_weights.json")
        result = MPFB_OT_SaveWeightsOperator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_reported('ERROR', "armature")
