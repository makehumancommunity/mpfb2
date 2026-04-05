"""Tests for the MakeTarget CreateTarget operator."""

import bpy
from .... import dynamic_import, ObjectService, TargetService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_CreateTargetOperator = dynamic_import("mpfb.ui.create_assets.maketarget.operators", "MPFB_OT_CreateTargetOperator")
MakeTargetObjectProperties = dynamic_import("mpfb.ui.create_assets.maketarget", "MakeTargetObjectProperties")


def test_create_target_is_registered():
    assert bpy.ops.mpfb.create_maketarget_target is not None
    assert MPFB_OT_CreateTargetOperator is not None


def test_create_target_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_CreateTargetOperator.poll(bpy.context)


def test_create_target_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_CreateTargetOperator.poll(bpy.context)


def test_create_target_errors_without_name():
    with HumanFixture() as fixture:
        # Ensure no name is set
        MakeTargetObjectProperties.set_value("name", "", entity_reference=fixture.basemesh)
        mockself = MockOperatorBase()
        result = MPFB_OT_CreateTargetOperator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_reported('ERROR', "Must specify the name")


def test_create_target_executes_successfully():
    with HumanFixture() as fixture:
        MakeTargetObjectProperties.set_value("name", "test_target", entity_reference=fixture.basemesh)
        mockself = MockOperatorBase()
        result = MPFB_OT_CreateTargetOperator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
        assert TargetService.has_target(fixture.basemesh, "test_target")
