"""Tests for MPFB_OT_Load_Library_Ink_Operator."""

import bpy
import os
from .... import ObjectService, LocationService, MaterialService, dynamic_import
from ..._helpers import MockOperatorBase, HumanFixture, BasemeshWithMakeSkinFixture

MPFB_OT_Load_Library_Ink_Operator = dynamic_import(
    "mpfb.ui.assetlibrary.operators.loadlibraryink",
    "MPFB_OT_Load_Library_Ink_Operator"
)


def test_operator_is_registered():
    assert bpy.ops.mpfb.load_library_ink is not None
    assert MPFB_OT_Load_Library_Ink_Operator is not None


def test_errors_when_no_basemesh():
    ObjectService.deselect_and_deactivate_all()
    mockself = MockOperatorBase(filepath="dummy.png")
    result = MPFB_OT_Load_Library_Ink_Operator.hardened_execute(mockself, bpy.context)
    assert result == {'CANCELLED'}
    mockself.mock_report.assert_reported('ERROR', 'No basemesh')


def test_errors_when_no_material():
    """A bare basemesh has no material — loading ink should report an error."""
    with HumanFixture() as fixture:
        mockself = MockOperatorBase(filepath="dummy.png")
        result = MPFB_OT_Load_Library_Ink_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'CANCELLED'}
        mockself.mock_report.assert_reported('ERROR', 'No material')


def test_errors_when_material_is_wrong_type():
    """A basemesh with a plain (non-MakeSkin) material should be rejected."""
    with HumanFixture() as fixture:
        # Add a plain Principled BSDF material that won't be identified as makeskin/layered_skin
        mat = bpy.data.materials.new(name="test_plain_material")
        mat.use_nodes = True
        fixture.basemesh.data.materials.append(mat)

        mockself = MockOperatorBase(filepath="dummy.png")
        result = MPFB_OT_Load_Library_Ink_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'CANCELLED'}
        mockself.mock_report.assert_reported('ERROR', 'Only MakeSkin')

        # Cleanup material
        fixture.basemesh.data.materials.clear()
        bpy.data.materials.remove(mat)


def test_load_ink_with_makeskin_material():
    """With a MakeSkin material and a valid ink JSON, the ink layer should load."""
    testdata = LocationService.get_mpfb_test("testdata")
    ink_json = os.path.join(testdata, "materials", "test_ink_layer.json")
    with BasemeshWithMakeSkinFixture() as fixture:
        mockself = MockOperatorBase(filepath=ink_json)
        result = MPFB_OT_Load_Library_Ink_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        # WARNING is acceptable if a proxy is present; errors are not
        errors = [r for r in mockself.mock_report.reports if r[0] == 'ERROR']
        assert not errors, f"Expected no errors, got: {errors}"
