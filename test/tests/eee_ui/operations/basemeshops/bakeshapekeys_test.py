"""Tests for the BasemeshOps Bake Shape Keys operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, BasemeshWithTargetFixture

MPFB_OT_Bake_Shapekeys_Operator = dynamic_import(
    "mpfb.ui.operations.basemeshops.operators.bakeshapekeys",
    "MPFB_OT_Bake_Shapekeys_Operator"
)


def test_bake_shapekeys_is_registered():
    assert bpy.ops.mpfb.bake_shapekeys is not None
    assert MPFB_OT_Bake_Shapekeys_Operator is not None


def test_bake_shapekeys_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Bake_Shapekeys_Operator.poll(bpy.context)


def test_bake_shapekeys_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Bake_Shapekeys_Operator.poll(bpy.context)


def test_bake_shapekeys_executes_with_basemesh():
    with HumanFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_Bake_Shapekeys_Operator.execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()


def test_bake_shapekeys_executes_with_target():
    with BasemeshWithTargetFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_Bake_Shapekeys_Operator.execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
