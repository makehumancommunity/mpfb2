"""Tests for the MakeClothes CheckClothes operator."""

import bpy
from .... import ObjectService, dynamic_import
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_CheckClothesOperator = dynamic_import("mpfb.ui.create_assets.makeclothes.operators", "MPFB_OT_CheckClothesOperator")


def test_check_clothes_is_registered():
    assert bpy.ops.mpfb.check_makeclothes_clothes is not None
    assert MPFB_OT_CheckClothesOperator is not None


def test_check_clothes_poll_true_with_active_object():
    with HumanFixture() as fixture:
        assert MPFB_OT_CheckClothesOperator.poll(bpy.context)


def test_check_clothes_errors_when_no_basemesh():
    """CheckClothes reports error when no basemesh is in the selection."""
    ObjectService.deselect_and_deactivate_all()
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object
    GeneralObjectProperties = dynamic_import("mpfb.entities.objectproperties", "GeneralObjectProperties")
    GeneralObjectProperties.set_value("object_type", "Clothes", entity_reference=cube)
    cube.select_set(True)
    mockself = MockOperatorBase()
    result = MPFB_OT_CheckClothesOperator.execute(mockself, bpy.context)
    assert result == {'CANCELLED'}
    mockself.mock_report.assert_reported('ERROR', 'basemesh')
    ObjectService.delete_object(cube)
