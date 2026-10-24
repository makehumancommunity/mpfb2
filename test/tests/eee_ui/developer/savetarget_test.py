"""Tests for the Developer SaveTarget operator."""

from types import SimpleNamespace

import bpy
from ... import dynamic_import, ObjectService
from .._helpers import HumanFixture, BasemeshWithTargetFixture

MPFB_OT_Save_Target_Operator = dynamic_import(
    "mpfb.ui.developer.operators.savetarget",
    "MPFB_OT_Save_Target_Operator"
)


def test_save_target_is_registered():
    assert bpy.ops.mpfb.save_target is not None
    assert MPFB_OT_Save_Target_Operator is not None


def test_get_active_key_returns_none_for_none():
    assert MPFB_OT_Save_Target_Operator.get_active_key(None) is None


def test_get_active_key_returns_none_when_object_has_no_data():
    assert MPFB_OT_Save_Target_Operator.get_active_key(SimpleNamespace()) is None
    assert MPFB_OT_Save_Target_Operator.get_active_key(SimpleNamespace(data=None)) is None


def test_get_active_key_returns_none_when_data_has_no_shape_keys():
    assert MPFB_OT_Save_Target_Operator.get_active_key(SimpleNamespace(data=SimpleNamespace())) is None
    assert MPFB_OT_Save_Target_Operator.get_active_key(
        SimpleNamespace(data=SimpleNamespace(shape_keys=None))) is None


def test_get_active_key_returns_none_for_basemesh_without_shape_keys():
    """This is the reported case: data.shape_keys is None, which used to raise on every redraw."""
    with HumanFixture() as fixture:
        fixture.basemesh.shape_key_clear()
        assert fixture.basemesh.data.shape_keys is None
        assert MPFB_OT_Save_Target_Operator.get_active_key(fixture.basemesh) is None


def test_save_target_poll_is_false_for_basemesh_without_shape_keys():
    with HumanFixture() as fixture:
        fixture.basemesh.shape_key_clear()
        ObjectService.activate_blender_object(fixture.basemesh)
        assert not MPFB_OT_Save_Target_Operator.poll(bpy.context)


def test_save_target_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Save_Target_Operator.poll(bpy.context)


def test_get_active_key_returns_the_active_key_block():
    with BasemeshWithTargetFixture() as fixture:
        basemesh = fixture.basemesh
        key_blocks = basemesh.data.shape_keys.key_blocks
        assert len(key_blocks) > 1
        basemesh.active_shape_key_index = len(key_blocks) - 1

        active_key = MPFB_OT_Save_Target_Operator.get_active_key(basemesh)
        assert active_key is not None
        assert active_key == key_blocks[len(key_blocks) - 1]


def test_save_target_poll_is_true_for_basemesh_with_an_active_target():
    with BasemeshWithTargetFixture() as fixture:
        basemesh = fixture.basemesh
        basemesh.active_shape_key_index = len(basemesh.data.shape_keys.key_blocks) - 1
        ObjectService.activate_blender_object(basemesh)
        assert MPFB_OT_Save_Target_Operator.poll(bpy.context)
