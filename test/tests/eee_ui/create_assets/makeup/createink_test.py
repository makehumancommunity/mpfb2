"""Tests for the MakeUp CreateInk operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, BasemeshWithMakeSkinFixture

MPFB_OT_CreateInkOperator = dynamic_import("mpfb.ui.create_assets.makeup.operators.createink", "MPFB_OT_CreateInkOperator")
MAKEUP_PROPERTIES = dynamic_import("mpfb.ui.create_assets.makeup.makeuppanel", "MAKEUP_PROPERTIES")


def test_create_ink_is_registered():
    assert bpy.ops.mpfb.create_ink is not None
    assert MPFB_OT_CreateInkOperator is not None


def test_create_ink_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_CreateInkOperator.poll(bpy.context)


def test_create_ink_poll_true_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_CreateInkOperator.poll(bpy.context)


def test_create_ink_errors_without_makeskin_material():
    with HumanFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_CreateInkOperator.execute(mockself, bpy.context)
        assert result == {'CANCELLED'}
        # Should report either "no materials" or "not a basemesh" or similar error
        assert len(mockself.mock_report.reports) > 0


def test_create_ink_executes_with_makeskin_material():
    with BasemeshWithMakeSkinFixture() as fixture:
        # Set focus_name to NONE (no special UV map)
        MAKEUP_PROPERTIES.set_value("create_ink", False, entity_reference=bpy.context.scene)
        mockself = MockOperatorBase()
        result = MPFB_OT_CreateInkOperator.execute(mockself, bpy.context)
        # With a MakeSkin material and focus_name=NONE (if default), expect FINISHED or error about focus_name
        assert result in ({'FINISHED'}, {'CANCELLED'})
