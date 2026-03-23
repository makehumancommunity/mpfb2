"""Tests for the MakeRig AutoTransferWeights operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, TwoHumansWithRigsFixture

MPFB_OT_Auto_Transfer_Weights_Operator = dynamic_import("mpfb.ui.create_assets.makerig.operators.autotransferweights", "MPFB_OT_Auto_Transfer_Weights_Operator")


def test_auto_transfer_weights_is_registered():
    assert bpy.ops.mpfb.auto_transfer_weights is not None
    assert MPFB_OT_Auto_Transfer_Weights_Operator is not None


def test_auto_transfer_weights_errors_without_two_armatures():
    with HumanFixture() as fixture:
        mockself = MockOperatorBase()
        # Only one object is selected/active, not two armatures
        result = MPFB_OT_Auto_Transfer_Weights_Operator.hardened_execute(mockself, bpy.context)
        # Should return CANCELED (not two armatures)
        assert result in ({'CANCELED'}, {'CANCELLED'})


def test_auto_transfer_weights_executes_with_two_rigs():
    with TwoHumansWithRigsFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_Auto_Transfer_Weights_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
