"""Tests for MPFB_OT_Unload_Library_Clothes_Operator."""

import bpy
import os
from .... import ObjectService, LocationService, dynamic_import
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Unload_Library_Clothes_Operator = dynamic_import(
    "mpfb.ui.assetlibrary.operators.unloadlibraryclothes",
    "MPFB_OT_Unload_Library_Clothes_Operator"
)
MPFB_OT_Load_Library_Clothes_Operator = dynamic_import(
    "mpfb.ui.assetlibrary.operators.loadlibraryclothes",
    "MPFB_OT_Load_Library_Clothes_Operator"
)
ASSET_SETTINGS_PROPERTIES = dynamic_import(
    "mpfb.ui.assetlibrary.assetsettingspanel",
    "ASSET_SETTINGS_PROPERTIES"
)
GeneralObjectProperties = dynamic_import(
    "mpfb.entities.objectproperties",
    "GeneralObjectProperties"
)


def test_operator_is_registered():
    assert bpy.ops.mpfb.unload_library_clothes is not None
    assert MPFB_OT_Unload_Library_Clothes_Operator is not None


def test_errors_when_no_matching_asset():
    with HumanFixture() as fixture:
        mockself = MockOperatorBase(filepath="nonexistent/dummy.mhclo")
        result = MPFB_OT_Unload_Library_Clothes_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_reported('ERROR', 'Could not find asset')


def test_unload_clothes_successfully():
    testdata = LocationService.get_mpfb_test("testdata")
    socks = os.path.join(testdata, "better_socks_low.mhclo")
    with HumanFixture() as fixture:
        ASSET_SETTINGS_PROPERTIES.set_value("set_up_rigging", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("fit_to_body", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("delete_group", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("interpolate_weights", False, entity_reference=bpy.context.scene)
        load_self = MockOperatorBase(filepath=socks, object_type="Clothes", material_type="MAKESKIN")
        MPFB_OT_Load_Library_Clothes_Operator.hardened_execute(load_self, bpy.context)

        clothes = ObjectService.find_object_of_type_amongst_nearest_relatives(fixture.basemesh, "Clothes")
        assert clothes is not None, "Clothes must be loaded before unload test"

        source = GeneralObjectProperties.get_value("asset_source", entity_reference=clothes)
        assert source, "Loaded clothes must have an asset_source property"

        ObjectService.activate_blender_object(fixture.basemesh)
        unload_self = MockOperatorBase(filepath=source)
        result = MPFB_OT_Unload_Library_Clothes_Operator.hardened_execute(unload_self, bpy.context)
        assert result == {'FINISHED'}
        unload_self.mock_report.assert_no_errors()

        remaining = ObjectService.find_object_of_type_amongst_nearest_relatives(fixture.basemesh, "Clothes")
        assert remaining is None, "Clothes should have been removed"
