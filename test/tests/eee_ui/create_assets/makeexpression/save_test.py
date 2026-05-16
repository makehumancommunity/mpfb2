"""Tests for the MakeExpression save operator."""

import bpy, os, json
from pytest import approx
from .... import dynamic_import, LocationService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Compose_Expression_Save_Operator = dynamic_import(
    "mpfb.ui.create_assets.makeexpression.operators.save",
    "MPFB_OT_Compose_Expression_Save_Operator",
)
MakeExpressionProperties = dynamic_import("mpfb.ui.create_assets.makeexpression", "MakeExpressionProperties")


def _reset_props():
    arkit = dynamic_import("mpfb.services.faceservice", "ARKIT_FACEUNITS")
    for name in arkit:
        MakeExpressionProperties.set_value(name, 0.0, entity_reference=bpy.context.scene)
    MakeExpressionProperties.set_value("expression_name", "", entity_reference=bpy.context.scene)
    MakeExpressionProperties.set_value("description", "", entity_reference=bpy.context.scene)
    MakeExpressionProperties.set_value("tags", "", entity_reference=bpy.context.scene)
    MakeExpressionProperties.set_value("author", "", entity_reference=bpy.context.scene)
    MakeExpressionProperties.set_value("copyright", "", entity_reference=bpy.context.scene)
    MakeExpressionProperties.set_value("license", "CC0", entity_reference=bpy.context.scene)
    MakeExpressionProperties.set_value("homepage", "", entity_reference=bpy.context.scene)
    MakeExpressionProperties.set_value("overwrite", True, entity_reference=bpy.context.scene)


def _expressions_root():
    return LocationService.get_user_data("expressions")


def _cleanup(filename):
    path = os.path.join(_expressions_root(), filename)
    if os.path.exists(path):
        os.remove(path)


def test_save_operator_is_registered():
    assert MPFB_OT_Compose_Expression_Save_Operator is not None
    assert bpy.ops.mpfb.compose_expression_save is not None


def test_save_rejects_empty_name():
    with HumanFixture():
        _reset_props()
        MakeExpressionProperties.set_value("expression_name", "", entity_reference=bpy.context.scene)
        MakeExpressionProperties.set_value("jawOpen", 0.5, entity_reference=bpy.context.scene)
        mockself = MockOperatorBase()
        MPFB_OT_Compose_Expression_Save_Operator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_reported('ERROR', "valid name")


def test_save_rejects_path_separator():
    with HumanFixture():
        _reset_props()
        MakeExpressionProperties.set_value("expression_name", "evil/name", entity_reference=bpy.context.scene)
        MakeExpressionProperties.set_value("jawOpen", 0.5, entity_reference=bpy.context.scene)
        mockself = MockOperatorBase()
        MPFB_OT_Compose_Expression_Save_Operator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_reported('ERROR', "without path")


def test_save_rejects_all_zero_sliders():
    with HumanFixture():
        _reset_props()
        MakeExpressionProperties.set_value("expression_name", "all-zero", entity_reference=bpy.context.scene)
        # leave sliders at 0.0
        mockself = MockOperatorBase()
        MPFB_OT_Compose_Expression_Save_Operator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_reported('ERROR', "non-zero")


def test_save_writes_json_file():
    fname = "mpfb-compose-test-saved.json"
    try:
        with HumanFixture():
            _reset_props()
            MakeExpressionProperties.set_value("expression_name", "mpfb-compose-test-saved", entity_reference=bpy.context.scene)
            MakeExpressionProperties.set_value("description", "A test expression", entity_reference=bpy.context.scene)
            MakeExpressionProperties.set_value("jawOpen", 0.6, entity_reference=bpy.context.scene)
            MakeExpressionProperties.set_value("mouthSmileLeft", 0.3, entity_reference=bpy.context.scene)

            mockself = MockOperatorBase()
            result = MPFB_OT_Compose_Expression_Save_Operator.hardened_execute(mockself, bpy.context)
            assert result == {'FINISHED'}
            mockself.mock_report.assert_no_errors()

            target_path = os.path.join(_expressions_root(), fname)
            assert os.path.exists(target_path)
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data["name"] == "mpfb-compose-test-saved"
            assert data["description"] == "A test expression"
            assert data["face_units"]["jawOpen"] == approx(0.6)
            assert data["face_units"]["mouthSmileLeft"] == approx(0.3)
            assert "browInnerUp" not in data["face_units"]
    finally:
        _cleanup(fname)


def test_save_respects_no_overwrite():
    fname = "mpfb-compose-test-no-overwrite.json"
    try:
        with HumanFixture():
            _reset_props()
            MakeExpressionProperties.set_value("expression_name", "mpfb-compose-test-no-overwrite", entity_reference=bpy.context.scene)
            MakeExpressionProperties.set_value("jawOpen", 0.4, entity_reference=bpy.context.scene)
            MakeExpressionProperties.set_value("overwrite", False, entity_reference=bpy.context.scene)

            mockself = MockOperatorBase()
            # First save creates the file.
            result = MPFB_OT_Compose_Expression_Save_Operator.hardened_execute(mockself, bpy.context)
            assert result == {'FINISHED'}
            target_path = os.path.join(_expressions_root(), fname)
            assert os.path.exists(target_path)

            # Second save with overwrite off must report an error.
            mockself2 = MockOperatorBase()
            MPFB_OT_Compose_Expression_Save_Operator.hardened_execute(mockself2, bpy.context)
            mockself2.mock_report.assert_reported('ERROR', "already exists")
    finally:
        _cleanup(fname)
