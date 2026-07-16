"""Tests for MPFB_OT_Load_Library_Material_Operator."""

import bpy
from .... import AssetService, ObjectService, dynamic_import
from ..._helpers import MockOperatorBase, HumanWithRigAndClothesFixture

MPFB_OT_Load_Library_Material_Operator = dynamic_import(
    "mpfb.ui.apply_assets.assetlibrary.operators.loadlibrarymaterial",
    "MPFB_OT_Load_Library_Material_Operator"
)

GeneralObjectProperties = dynamic_import("mpfb.entities.objectproperties", "GeneralObjectProperties")

# The clothes fixture loads its mhclo from testdata, which is not an asset root. Point the
# asset source at an installed asset instead, so that the default material can be resolved.
_INSTALLED_ASSET = "fedora01/fedora01.mhclo"


def _activate_clothes(fixture):
    clothes = fixture.clothes
    ObjectService.activate_blender_object(clothes)
    GeneralObjectProperties.set_value("asset_source", _INSTALLED_ASSET, entity_reference=clothes)
    return clothes


def test_operator_is_registered():
    assert bpy.ops.mpfb.load_library_material is not None
    assert MPFB_OT_Load_Library_Material_Operator is not None


def test_load_material_sets_alternative_material_property():
    """Loading a material via filepath applies it and records the fragment on the object."""
    with HumanWithRigAndClothesFixture() as fixture:
        clothes = _activate_clothes(fixture)

        material = AssetService.find_asset_absolute_path("materials/brown.mhmat", "eyes")
        assert material, "Expected the bundled brown eyes material to be installed"

        mockself = MockOperatorBase(filepath=material, restore_default=False)
        result = MPFB_OT_Load_Library_Material_Operator.hardened_execute(mockself, bpy.context)

        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()

        fragment = GeneralObjectProperties.get_value("alternative_material", entity_reference=clothes)
        assert fragment == "materials/brown.mhmat", "The alternative material fragment should have been recorded"


def test_restore_default_clears_alternative_material_property():
    """Restoring the default material re-applies the mhclo material and clears the property."""
    with HumanWithRigAndClothesFixture() as fixture:
        clothes = _activate_clothes(fixture)

        GeneralObjectProperties.set_value("alternative_material", "materials/brown.mhmat", entity_reference=clothes)

        mockself = MockOperatorBase(filepath="", restore_default=True)
        result = MPFB_OT_Load_Library_Material_Operator.hardened_execute(mockself, bpy.context)

        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()

        fragment = GeneralObjectProperties.get_value("alternative_material", entity_reference=clothes)
        assert not fragment, "The alternative material fragment should have been cleared"


def test_restore_default_without_asset_source_is_cancelled():
    """An object which did not come from the asset library has no default material to restore."""
    with HumanWithRigAndClothesFixture() as fixture:
        clothes = fixture.clothes
        ObjectService.activate_blender_object(clothes)
        GeneralObjectProperties.set_value("asset_source", "", entity_reference=clothes)

        mockself = MockOperatorBase(filepath="", restore_default=True)
        result = MPFB_OT_Load_Library_Material_Operator.hardened_execute(mockself, bpy.context)

        assert result == {'CANCELLED'}
        mockself.mock_report.assert_reported('ERROR', "default material")


def test_load_material_with_bogus_filepath_is_cancelled():
    """A filepath which does not exist should be reported rather than silently ignored."""
    with HumanWithRigAndClothesFixture() as fixture:
        _activate_clothes(fixture)

        mockself = MockOperatorBase(filepath="/no/such/material.mhmat", restore_default=False)
        result = MPFB_OT_Load_Library_Material_Operator.hardened_execute(mockself, bpy.context)

        assert result == {'CANCELLED'}
        mockself.mock_report.assert_reported('ERROR', "Could not find alternative material")
