"""Tests for MPFB_OT_Load_Library_Clothes_Operator."""

import bpy
import os
from .... import ObjectService, HumanService, LocationService, dynamic_import
from ..._helpers import MockOperatorBase, HumanFixture, HumanWithRigFixture

MPFB_OT_Load_Library_Clothes_Operator = dynamic_import(
    "mpfb.ui.apply_assets.assetlibrary.operators.loadlibraryclothes",
    "MPFB_OT_Load_Library_Clothes_Operator"
)
ASSET_SETTINGS_PROPERTIES = dynamic_import(
    "mpfb.ui.apply_assets.assetlibrary.assetsettingspanel",
    "ASSET_SETTINGS_PROPERTIES"
)


def test_operator_is_registered():
    assert bpy.ops.mpfb.load_library_clothes is not None
    assert MPFB_OT_Load_Library_Clothes_Operator is not None


def test_errors_when_fit_to_body_enabled_without_basemesh():
    ObjectService.deselect_and_deactivate_all()
    ASSET_SETTINGS_PROPERTIES.set_value("fit_to_body", True, entity_reference=bpy.context.scene)
    mockself = MockOperatorBase(filepath="dummy.mhclo", object_type="Clothes", material_type="MAKESKIN")
    result = MPFB_OT_Load_Library_Clothes_Operator.hardened_execute(mockself, bpy.context)
    ASSET_SETTINGS_PROPERTIES.set_value("fit_to_body", False, entity_reference=bpy.context.scene)
    assert result == {'FINISHED'}
    mockself.mock_report.assert_reported('ERROR', 'Fit to body')


def test_load_library_clothes_without_rig():
    testdata = LocationService.get_mpfb_test("testdata")
    socks = os.path.join(testdata, "better_socks_low.mhclo")
    with HumanFixture() as fixture:
        ASSET_SETTINGS_PROPERTIES.set_value("set_up_rigging", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("fit_to_body", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("delete_group", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("interpolate_weights", False, entity_reference=bpy.context.scene)
        mockself = MockOperatorBase(filepath=socks, object_type="Clothes", material_type="MAKESKIN")
        result = MPFB_OT_Load_Library_Clothes_Operator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_no_errors()
        assert result == {'FINISHED'}
        clothes = ObjectService.find_object_of_type_amongst_nearest_relatives(fixture.basemesh, "Clothes")
        assert clothes is not None, "Clothes should be loaded"


def test_load_library_clothes_with_rig():
    testdata = LocationService.get_mpfb_test("testdata")
    socks = os.path.join(testdata, "better_socks_low.mhclo")
    with HumanWithRigFixture() as fixture:
        ASSET_SETTINGS_PROPERTIES.set_value("set_up_rigging", True, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("fit_to_body", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("delete_group", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("interpolate_weights", False, entity_reference=bpy.context.scene)
        mockself = MockOperatorBase(filepath=socks, object_type="Clothes", material_type="MAKESKIN")
        result = MPFB_OT_Load_Library_Clothes_Operator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_no_errors()
        assert result == {'FINISHED'}
        clothes = ObjectService.find_object_of_type_amongst_nearest_relatives(fixture.basemesh, "Clothes")
        assert clothes is not None, "Clothes should be loaded"
        assert clothes.parent == fixture.rig, "Clothes should be parented to the rig"
