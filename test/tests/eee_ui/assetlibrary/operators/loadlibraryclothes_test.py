"""Tests for MPFB_OT_Load_Library_Clothes_Operator."""

import bpy
import os
import shutil
from .... import ObjectService, HumanService, LocationService, MaterialService, dynamic_import
from ..._helpers import MockOperatorBase, HumanFixture, HumanWithRigFixture

MPFB_OT_Load_Library_Clothes_Operator = dynamic_import(
    "mpfb.ui.apply_assets.assetlibrary.operators.loadlibraryclothes",
    "MPFB_OT_Load_Library_Clothes_Operator"
)
ASSET_SETTINGS_PROPERTIES = dynamic_import(
    "mpfb.ui.apply_assets.assetlibrary.assetsettingspanel",
    "ASSET_SETTINGS_PROPERTIES"
)


def _write_broken_mhclo(dest_dir):
    """Copy the socks fixture into dest_dir, with its material line pointed at a nonexistent file."""
    testdata = LocationService.get_mpfb_test("testdata")
    shutil.copy(os.path.join(testdata, "better_socks_low.obj"), str(dest_dir))
    with open(os.path.join(testdata, "better_socks_low.mhclo"), "r", encoding="utf8") as handle:
        content = handle.read()
    assert "material better_socks_low.mhmat" in content
    content = content.replace("material better_socks_low.mhmat", "material no_such_material.mhmat")
    broken = os.path.join(str(dest_dir), "broken_material.mhclo")
    with open(broken, "w", encoding="utf8") as handle:
        handle.write(content)
    return broken


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


def test_load_library_clothes_warns_on_missing_material(tmp_path):
    """The operator warns, rather than crashing, when the mhclo points at a missing mhmat"""
    broken = _write_broken_mhclo(tmp_path)
    with HumanFixture() as fixture:
        ASSET_SETTINGS_PROPERTIES.set_value("set_up_rigging", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("fit_to_body", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("delete_group", False, entity_reference=bpy.context.scene)
        ASSET_SETTINGS_PROPERTIES.set_value("interpolate_weights", False, entity_reference=bpy.context.scene)
        mockself = MockOperatorBase(filepath=broken, object_type="Clothes", material_type="MAKESKIN")
        # Before issue 420 was fixed, this raised FileNotFoundError
        result = MPFB_OT_Load_Library_Clothes_Operator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_no_errors()
        assert result == {'FINISHED'}
        mockself.mock_report.assert_reported('WARNING', "no_such_material.mhmat")
        clothes = ObjectService.find_object_of_type_amongst_nearest_relatives(fixture.basemesh, "Clothes")
        assert clothes is not None, "Clothes should have been loaded despite the missing material"
        assert not MaterialService.has_materials(clothes), "A missing material should mean no material at all"
