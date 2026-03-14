"""Tests for the MakeRig MoveToCube operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, HumanWithRigFixture

MPFB_OT_Move_To_Cube_Operator = dynamic_import("mpfb.ui.create_assets.makerig.operators.movetocube", "MPFB_OT_Move_To_Cube_Operator")


def test_move_bone_to_cube_is_registered():
    assert bpy.ops.mpfb.move_bone_to_cube is not None
    assert MPFB_OT_Move_To_Cube_Operator is not None


def test_move_bone_to_cube_errors_without_armature():
    with HumanFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_Move_To_Cube_Operator.hardened_execute(mockself, bpy.context)
        assert result in ({'CANCELED'}, {'CANCELLED'})
        mockself.mock_report.assert_reported('ERROR', "armature")


def test_move_bone_to_cube_errors_not_in_edit_mode():
    with HumanWithRigFixture() as fixture:
        mockself = MockOperatorBase()
        # Active object is the rig in object mode (not edit mode)
        result = MPFB_OT_Move_To_Cube_Operator.hardened_execute(mockself, bpy.context)
        assert result in ({'CANCELED'}, {'CANCELLED'})
        # Either "Edit mode only" or "Select basemesh too" depending on setup
        assert len(mockself.mock_report.reports) > 0
