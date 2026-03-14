"""Tests for the MakeUp CreateUvMap operator."""

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_CreateUvMapOperator = dynamic_import("mpfb.ui.create_assets.makeup.operators.createuvmap", "MPFB_OT_CreateUvMapOperator")
MAKEUP_PROPERTIES = dynamic_import("mpfb.ui.create_assets.makeup.makeuppanel", "MAKEUP_PROPERTIES")


def test_create_uv_map_is_registered():
    assert bpy.ops.mpfb.create_uv_map is not None
    assert MPFB_OT_CreateUvMapOperator is not None


def test_create_uv_map_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_CreateUvMapOperator.poll(bpy.context)


def test_create_uv_map_poll_true_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_CreateUvMapOperator.poll(bpy.context)


def test_create_uv_map_execute_creates_uv_map():
    with HumanFixture() as fixture:
        MAKEUP_PROPERTIES.set_value("uv_map_name", "test_uv_map", entity_reference=bpy.context.scene)
        mockself = MockOperatorBase()
        result = MPFB_OT_CreateUvMapOperator.execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        assert "test_uv_map" in fixture.basemesh.data.uv_layers


def test_create_uv_map_execute_cancelled_if_already_exists():
    with HumanFixture() as fixture:
        MAKEUP_PROPERTIES.set_value("uv_map_name", "test_uv_map2", entity_reference=bpy.context.scene)
        mockself = MockOperatorBase()
        # Create the UV map first
        MPFB_OT_CreateUvMapOperator.execute(mockself, bpy.context)
        # Try to create it again
        mockself2 = MockOperatorBase()
        result2 = MPFB_OT_CreateUvMapOperator.execute(mockself2, bpy.context)
        assert result2 == {'CANCELLED'}
