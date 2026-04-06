"""Tests for MPFB_OT_Load_Library_Skin_Operator."""

import bpy
import os
from .... import ObjectService, LocationService, dynamic_import
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Load_Library_Skin_Operator = dynamic_import(
    "mpfb.ui.assetlibrary.operators.loadlibraryskin",
    "MPFB_OT_Load_Library_Skin_Operator"
)
ASSET_SETTINGS_PROPERTIES = dynamic_import(
    "mpfb.ui.assetlibrary.assetsettingspanel",
    "ASSET_SETTINGS_PROPERTIES"
)


def test_operator_is_registered():
    assert bpy.ops.mpfb.load_library_skin is not None
    assert MPFB_OT_Load_Library_Skin_Operator is not None


def test_load_skin_on_basemesh():
    testdata = LocationService.get_mpfb_test("testdata")
    mhmat = os.path.join(testdata, "better_socks_low.mhmat")
    with HumanFixture() as fixture:
        ASSET_SETTINGS_PROPERTIES.set_value("skin_type", "MAKESKIN", entity_reference=bpy.context.scene)
        mockself = MockOperatorBase(filepath=mhmat)
        result = MPFB_OT_Load_Library_Skin_Operator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_no_errors()
        assert result == {'FINISHED'}
