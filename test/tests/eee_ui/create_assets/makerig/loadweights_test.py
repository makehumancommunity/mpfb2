"""Tests for the MakeRig LoadWeights operator."""

import bpy
from .... import dynamic_import, ObjectService, LocationService
from ..._helpers import MockOperatorBase, HumanFixture, HumanWithRigFixture

MPFB_OT_Load_Weights_Operator = dynamic_import("mpfb.ui.create_assets.makerig.operators.loadweights", "MPFB_OT_Load_Weights_Operator")


def test_load_weights_is_registered():
    assert bpy.ops.mpfb.load_weights is not None
    assert MPFB_OT_Load_Weights_Operator is not None


def test_load_weights_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Load_Weights_Operator.poll(bpy.context)


def test_load_weights_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Load_Weights_Operator.poll(bpy.context)


def test_load_weights_errors_without_skeleton():
    with HumanFixture() as fixture:
        weights_path = LocationService.get_mpfb_data("rigs/standard/weights.default.json")
        mockself = MockOperatorBase(filepath=weights_path)
        result = MPFB_OT_Load_Weights_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_reported('ERROR', "skeleton")


def test_load_weights_executes_with_rig():
    with HumanWithRigFixture() as fixture:
        ObjectService.activate_blender_object(fixture.basemesh)
        weights_path = LocationService.get_mpfb_data("rigs/standard/weights.default.json")
        mockself = MockOperatorBase(filepath=weights_path)
        result = MPFB_OT_Load_Weights_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
