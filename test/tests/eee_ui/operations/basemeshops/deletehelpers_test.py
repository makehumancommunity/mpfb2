"""Tests for the BasemeshOps Delete Helpers operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Delete_Helpers_Operator = dynamic_import(
    "mpfb.ui.operations.basemeshops.operators.deletehelpers",
    "MPFB_OT_Delete_Helpers_Operator"
)


def test_delete_helpers_is_registered():
    assert bpy.ops.mpfb.delete_helpers is not None
    assert MPFB_OT_Delete_Helpers_Operator is not None


def test_delete_helpers_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Delete_Helpers_Operator.poll(bpy.context)


def test_delete_helpers_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Delete_Helpers_Operator.poll(bpy.context)


def test_delete_helpers_executes_with_basemesh():
    with HumanFixture() as fixture:
        # Operator uses self._delete_vertex_group() — requires real operator instance via bpy.ops
        result = bpy.ops.mpfb.delete_helpers()
        assert result == {'FINISHED'}
