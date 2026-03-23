"""Tests for the MakeClothes MarkClothes operator."""

import bpy
from .... import ObjectService, dynamic_import
from ..._helpers import MockOperatorBase, HumanFixture

MAKECLOTHES_PROPERTIES = dynamic_import("mpfb.ui.create_assets.makeclothes.makeclothespanel", "MAKECLOTHES_PROPERTIES")
MPFB_OT_MarkClothesOperator = dynamic_import("mpfb.ui.create_assets.makeclothes.operators", "MPFB_OT_MarkClothesOperator")


def test_mark_clothes_is_registered():
    assert bpy.ops.mpfb.mark_makeclothes_clothes is not None
    assert MPFB_OT_MarkClothesOperator is not None


def test_mark_clothes_poll_true_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_MarkClothesOperator.poll(bpy.context)


def test_mark_clothes_sets_object_type():
    """MarkClothes operator sets GeneralObjectProperties.object_type on active mesh."""
    with HumanFixture() as fixture:
        bpy.ops.mesh.primitive_cube_add()
        clothes_mesh = bpy.context.active_object
        ObjectService.activate_blender_object(clothes_mesh)
        MAKECLOTHES_PROPERTIES.set_value("object_type", "Clothes", entity_reference=bpy.context.scene)
        mockself = MockOperatorBase()
        result = MPFB_OT_MarkClothesOperator.execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
        GeneralObjectProperties = dynamic_import("mpfb.entities.objectproperties", "GeneralObjectProperties")
        obj_type = GeneralObjectProperties.get_value("object_type", entity_reference=clothes_mesh)
        assert obj_type == "Clothes"
        ObjectService.delete_object(clothes_mesh)
