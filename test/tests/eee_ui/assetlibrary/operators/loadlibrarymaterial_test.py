"""Tests for MPFB_OT_Load_Library_Material_Operator."""

import bpy
from .... import ObjectService, dynamic_import
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Load_Library_Material_Operator = dynamic_import(
    "mpfb.ui.apply_assets.assetlibrary.operators.loadlibrarymaterial",
    "MPFB_OT_Load_Library_Material_Operator"
)


def test_operator_is_registered():
    assert bpy.ops.mpfb.load_library_material is not None
    assert MPFB_OT_Load_Library_Material_Operator is not None


def test_executes_with_default_material_selected():
    """When no alternative material is chosen (DEFAULT), the operator is a no-op and finishes cleanly."""
    with HumanFixture() as fixture:
        mockself = MockOperatorBase()
        result = MPFB_OT_Load_Library_Material_Operator.hardened_execute(mockself, bpy.context)
        # DEFAULT path: just reports INFO, no error
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()
