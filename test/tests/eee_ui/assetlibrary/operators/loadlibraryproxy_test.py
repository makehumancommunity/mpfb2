"""Tests for MPFB_OT_Load_Library_Proxy_Operator."""

import bpy
import os
from .... import ObjectService, LocationService, dynamic_import
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Load_Library_Proxy_Operator = dynamic_import(
    "mpfb.ui.apply_assets.assetlibrary.operators.loadlibraryproxy",
    "MPFB_OT_Load_Library_Proxy_Operator"
)
ASSET_SETTINGS_PROPERTIES = dynamic_import(
    "mpfb.ui.apply_assets.assetlibrary.assetsettingspanel",
    "ASSET_SETTINGS_PROPERTIES"
)


def test_operator_is_registered():
    assert bpy.ops.mpfb.load_library_proxy is not None
    assert MPFB_OT_Load_Library_Proxy_Operator is not None


def test_errors_when_rigging_enabled_without_rig():
    testdata = LocationService.get_mpfb_test("testdata")
    socks = os.path.join(testdata, "better_socks_low.mhclo")
    with HumanFixture() as fixture:
        ASSET_SETTINGS_PROPERTIES.set_value("set_up_rigging", True, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("fit_to_body", False, entity_reference=bpy.context.scene)
        mockself = MockOperatorBase(filepath=socks, object_type="Proxymeshes")
        result = MPFB_OT_Load_Library_Proxy_Operator.hardened_execute(mockself, bpy.context)
        ASSET_SETTINGS_PROPERTIES.set_value("set_up_rigging", False, entity_reference=bpy.context.scene)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_reported('ERROR', 'set up rigging')


def test_load_proxy_without_options():
    """Loading a proxy with all options disabled: operator reports no errors and a new Proxymeshes object appears in the scene."""
    testdata = LocationService.get_mpfb_test("testdata")
    socks = os.path.join(testdata, "better_socks_low.mhclo")
    GeneralObjectProperties = dynamic_import("mpfb.entities.objectproperties", "GeneralObjectProperties")
    with HumanFixture() as fixture:
        ASSET_SETTINGS_PROPERTIES.set_value("fit_to_body", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("set_up_rigging", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("mask_base_mesh", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("delete_group", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("interpolate_weights", False, entity_reference=bpy.context.scene)
        mockself = MockOperatorBase(filepath=socks, object_type="Proxymeshes")
        result = MPFB_OT_Load_Library_Proxy_Operator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_no_errors()
        assert result == {'FINISHED'}
        # Without rigging the proxy is not parented; find it by its object_type property
        proxy_found = any(
            GeneralObjectProperties.get_value("object_type", entity_reference=obj) == "Proxymeshes"
            for obj in bpy.data.objects
            if obj.type == 'MESH'
        )
        assert proxy_found, "A Proxymeshes object should have been created"
