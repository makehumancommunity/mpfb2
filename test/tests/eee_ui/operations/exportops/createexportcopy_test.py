"""Tests for the ExportOps Create Export Copy operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture, HumanWithRigFixture

MPFB_OT_Create_Export_Copy_Operator = dynamic_import(
    "mpfb.ui.operations.exportops.operators.createexportcopy",
    "MPFB_OT_Create_Export_Copy_Operator"
)


def test_create_export_copy_is_registered():
    assert bpy.ops.mpfb.export_copy is not None
    assert MPFB_OT_Create_Export_Copy_Operator is not None


def test_create_export_copy_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Create_Export_Copy_Operator.poll(bpy.context)


def test_create_export_copy_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Create_Export_Copy_Operator.poll(bpy.context)

# TODO: Need to work around mpfboperator for actual functionality test


