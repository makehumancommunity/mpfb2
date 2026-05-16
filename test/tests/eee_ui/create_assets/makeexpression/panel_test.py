"""Tests for the MakeExpression panel and scene-property registration."""

import bpy
from .... import dynamic_import

MakeExpressionProperties = dynamic_import("mpfb.ui.create_assets.makeexpression", "MakeExpressionProperties")


def test_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_MakeExpression_Panel')


def test_panel_parent_is_create_panel():
    assert bpy.types.MPFB_PT_MakeExpression_Panel.bl_parent_id == "MPFB_PT_Create_Panel"


def test_panel_label_is_makeexpression():
    assert bpy.types.MPFB_PT_MakeExpression_Panel.bl_label == "MakeExpression"


def test_scene_properties_are_registered():
    assert MakeExpressionProperties is not None


def test_all_arkit_sliders_registered_on_scene():
    """Every ARKit face unit has a corresponding scene property registered."""
    arkit = dynamic_import("mpfb.services.faceservice", "ARKIT_FACEUNITS")
    for face_unit_name in arkit:
        assert hasattr(bpy.types.Scene, "MPFB_EX_" + face_unit_name), \
            f"Missing scene property for {face_unit_name}"


def test_metadata_properties_registered_on_scene():
    """Metadata fields are registered on the scene."""
    for field in ["expression_name", "description", "tags", "author", "copyright",
                  "license", "homepage", "overwrite", "available_expression"]:
        assert hasattr(bpy.types.Scene, "MPFB_EX_" + field), f"Missing scene property MPFB_EX_{field}"
