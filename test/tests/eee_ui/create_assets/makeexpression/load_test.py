"""Tests for the MakeExpression load operator."""

import bpy, os, json
from pytest import approx
from .... import dynamic_import, FaceService, LocationService, TargetService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Compose_Expression_Load_Operator = dynamic_import(
    "mpfb.ui.create_assets.makeexpression.operators.load",
    "MPFB_OT_Compose_Expression_Load_Operator",
)
MakeExpressionProperties = dynamic_import("mpfb.ui.create_assets.makeexpression", "MakeExpressionProperties")
write_slider_values = dynamic_import("mpfb.ui.create_assets.makeexpression", "write_slider_values")


def test_load_operator_is_registered():
    assert MPFB_OT_Compose_Expression_Load_Operator is not None
    assert bpy.ops.mpfb.compose_expression_load is not None


def test_load_via_direct_call_writes_slider_values_and_shape_keys(tmp_path):
    """Exercise the load body directly (bypassing the enum). Verifies the bulk slider write +
    set_expression flow that the operator delegates to."""
    target_path = tmp_path / "smile.json"
    payload = {
        "format_version": 1,
        "name": "smile",
        "description": "A subtle smile",
        "tags": ["happy"],
        "face_units": {"mouthSmileLeft": 0.4, "mouthSmileRight": 0.4, "jawOpen": 0.2},
    }
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(payload, f)

    with HumanFixture() as fixture:
        # Pre-fabricate the !ex- shape keys so set_expression doesn't try to load real targets.
        for sk_name in ["!ex-mouthSmileLeft", "!ex-mouthSmileRight", "!ex-jawOpen"]:
            TargetService.create_shape_key(fixture.basemesh, sk_name, also_create_basis=False)
            fixture.basemesh.data.shape_keys.key_blocks[sk_name].value = 0.0

        expression_dict, metadata = FaceService.load_expression(str(target_path))
        zero_dict = {n: 0.0 for n in expression_dict.keys()}
        write_slider_values(bpy.context.scene, zero_dict)
        write_slider_values(bpy.context.scene, expression_dict)
        FaceService.clear_expression(fixture.basemesh)
        FaceService.set_expression(fixture.basemesh, expression_dict)

        assert MakeExpressionProperties.get_value("mouthSmileLeft", entity_reference=bpy.context.scene) == approx(0.4)
        assert MakeExpressionProperties.get_value("jawOpen", entity_reference=bpy.context.scene) == approx(0.2)
        assert fixture.basemesh.data.shape_keys.key_blocks["!ex-mouthSmileLeft"].value == approx(0.4)
        assert fixture.basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.2)


def test_load_operator_via_user_data():
    """Run the load operator end-to-end. Writes the JSON to user_data/expressions, picks it up
    via the dynamic enum, runs the operator, and cleans up."""
    expressions_root = LocationService.get_user_data("expressions")
    os.makedirs(expressions_root, exist_ok=True)
    test_name = "mpfb-compose-test-load"
    json_path = os.path.join(expressions_root, test_name + ".json")
    payload = {
        "format_version": 1,
        "name": test_name,
        "face_units": {"jawOpen": 0.3, "mouthSmileLeft": 0.5},
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f)

    try:
        with HumanFixture() as fixture:
            # Pre-fabricate the relevant !ex- shape keys to avoid pack dependency.
            for sk_name in ["!ex-jawOpen", "!ex-mouthSmileLeft"]:
                TargetService.create_shape_key(fixture.basemesh, sk_name, also_create_basis=False)
                fixture.basemesh.data.shape_keys.key_blocks[sk_name].value = 0.0

            # The enum's items_callback scans the directory; the path is the enum value.
            MakeExpressionProperties.set_value(
                "available_expression", json_path, entity_reference=bpy.context.scene)

            mockself = MockOperatorBase()
            result = MPFB_OT_Compose_Expression_Load_Operator.hardened_execute(mockself, bpy.context)
            assert result == {'FINISHED'}
            mockself.mock_report.assert_no_errors()

            assert MakeExpressionProperties.get_value("jawOpen", entity_reference=bpy.context.scene) == approx(0.3)
            assert MakeExpressionProperties.get_value("mouthSmileLeft", entity_reference=bpy.context.scene) == approx(0.5)
            assert fixture.basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.3)
            assert fixture.basemesh.data.shape_keys.key_blocks["!ex-mouthSmileLeft"].value == approx(0.5)
    finally:
        if os.path.exists(json_path):
            os.remove(json_path)
