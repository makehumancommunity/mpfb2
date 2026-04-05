"""Tests for the MakeClothes GenerateUUID operator."""

import bpy
from .... import ObjectService, dynamic_import
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_GenerateUUIDOperator = dynamic_import("mpfb.ui.create_assets.makeclothes.operators", "MPFB_OT_GenerateUUIDOperator")


def test_genuuid_is_registered():
    assert bpy.ops.mpfb.genuuid is not None
    assert MPFB_OT_GenerateUUIDOperator is not None


def test_generate_uuid_errors_when_no_clothes_selected():
    """GenerateUUID reports error when no non-basemesh object is selected."""
    with HumanFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_GenerateUUIDOperator.hardened_execute(mockself, bpy.context)
        assert result == {'CANCELED'}
        mockself.mock_report.assert_reported('ERROR', 'No clothes')


def test_generate_uuid_sets_uuid_on_clothes():
    """GenerateUUID sets a valid UUID string on the clothes object."""
    with HumanFixture() as fixture:
        bpy.ops.mesh.primitive_cube_add()
        clothes_mesh = bpy.context.active_object
        GeneralObjectProperties = dynamic_import("mpfb.entities.objectproperties", "GeneralObjectProperties")
        GeneralObjectProperties.set_value("object_type", "Clothes", entity_reference=clothes_mesh)
        fixture.basemesh.select_set(False)
        clothes_mesh.select_set(True)
        ObjectService.activate_blender_object(clothes_mesh)
        mockself = MockOperatorBase()
        result = MPFB_OT_GenerateUUIDOperator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
        uuid_val = GeneralObjectProperties.get_value("uuid", entity_reference=clothes_mesh)
        assert uuid_val and len(uuid_val) == 36
        ObjectService.delete_object(clothes_mesh)
