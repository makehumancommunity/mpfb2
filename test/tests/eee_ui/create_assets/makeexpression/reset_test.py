"""Tests for the MakeExpression reset operator."""

import bpy
from pytest import approx
from .... import dynamic_import, ObjectService, TargetService, FaceService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Compose_Expression_Reset_Operator = dynamic_import(
    "mpfb.ui.create_assets.makeexpression.operators.reset",
    "MPFB_OT_Compose_Expression_Reset_Operator",
)
MakeExpressionProperties = dynamic_import("mpfb.ui.create_assets.makeexpression", "MakeExpressionProperties")


def test_reset_operator_is_registered():
    assert MPFB_OT_Compose_Expression_Reset_Operator is not None
    assert bpy.ops.mpfb.compose_expression_reset is not None


def test_reset_zeroes_existing_expression_shape_keys():
    """Reset zeroes any !ex- shape keys on the basemesh and resets all sliders to 0.0."""
    with HumanFixture() as fixture:
        # Fabricate two !ex- shape keys with non-zero values.
        TargetService.create_shape_key(fixture.basemesh, "!ex-jawOpen", also_create_basis=False)
        TargetService.create_shape_key(fixture.basemesh, "!ex-mouthSmileLeft", also_create_basis=False)
        fixture.basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value = 0.7
        fixture.basemesh.data.shape_keys.key_blocks["!ex-mouthSmileLeft"].value = 0.4

        # Set the sliders too. Setting via set_value triggers the per-slider update callback,
        # which will write back to the !ex- shape keys — that's fine, the values match.
        MakeExpressionProperties.set_value("jawOpen", 0.7, entity_reference=bpy.context.scene)
        MakeExpressionProperties.set_value("mouthSmileLeft", 0.4, entity_reference=bpy.context.scene)

        mockself = MockOperatorBase()
        result = MPFB_OT_Compose_Expression_Reset_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}

        assert fixture.basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.0)
        assert fixture.basemesh.data.shape_keys.key_blocks["!ex-mouthSmileLeft"].value == approx(0.0)
        assert MakeExpressionProperties.get_value("jawOpen", entity_reference=bpy.context.scene) == approx(0.0)
        assert MakeExpressionProperties.get_value("mouthSmileLeft", entity_reference=bpy.context.scene) == approx(0.0)
