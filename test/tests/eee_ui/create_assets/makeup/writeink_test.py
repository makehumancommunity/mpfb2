"""Tests for the MakeUp WriteInk operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_WriteInkOperator = dynamic_import("mpfb.ui.create_assets.makeup.operators.writeink", "MPFB_OT_WriteInkOperator")
MAKEUP_PROPERTIES = dynamic_import("mpfb.ui.create_assets.makeup.makeuppanel", "MAKEUP_PROPERTIES")


def test_write_ink_layer_is_registered():
    assert bpy.ops.mpfb.write_ink_layer is not None
    assert MPFB_OT_WriteInkOperator is not None


def test_write_ink_layer_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_WriteInkOperator.poll(bpy.context)


def test_write_ink_layer_poll_true_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_WriteInkOperator.poll(bpy.context)


def test_write_ink_layer_errors_without_ink_layer_name():
    with HumanFixture() as fixture:
        MAKEUP_PROPERTIES.set_value("ink_layer_name", "", entity_reference=bpy.context.scene)
        mockself = MockOperatorBase()
        result = MPFB_OT_WriteInkOperator.hardened_execute(mockself, bpy.context)
        assert result == {'CANCELLED'}
        mockself.mock_report.assert_reported('ERROR', "ink layer name")


def test_write_ink_layer_errors_not_basemesh():
    with HumanFixture() as fixture:
        MAKEUP_PROPERTIES.set_value("ink_layer_name", "test_ink", entity_reference=bpy.context.scene)
        # The basemesh IS a basemesh, but has no material
        mockself = MockOperatorBase()
        result = MPFB_OT_WriteInkOperator.hardened_execute(mockself, bpy.context)
        assert result == {'CANCELLED'}
        # Should report error about no materials or no MakeSkin material
        assert len(mockself.mock_report.reports) > 0
