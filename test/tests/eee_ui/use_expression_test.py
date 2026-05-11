"""Operator-level tests for the use-expression panel.

These tests fabricate `!ex-*` shape keys without geometric content so they run without the
`faceunits01` asset pack — mirroring the pattern in `bbb_services/faceservice_test.py`. The
faceunits01-installed probe is monkey-patched to True so the operators don't refuse to run.
"""

import json, os
import bpy
from pytest import approx
from .. import AssetService
from .. import FaceService
from .. import HumanService
from .. import ObjectService
from .. import TargetService
from .. import dynamic_import
from ._helpers import MockOperatorBase

MPFB_OT_Apply_Expression_Operator = dynamic_import(
    "mpfb.ui.apply_assets.useexpression.operators.applyexpression",
    "MPFB_OT_Apply_Expression_Operator",
)
MPFB_OT_Set_Expression_Weight_Operator = dynamic_import(
    "mpfb.ui.apply_assets.useexpression.operators.setexpressionweight",
    "MPFB_OT_Set_Expression_Weight_Operator",
)
MPFB_OT_Remove_Expression_Operator = dynamic_import(
    "mpfb.ui.apply_assets.useexpression.operators.removeexpression",
    "MPFB_OT_Remove_Expression_Operator",
)
MPFB_OT_Clear_Expression_Operator = dynamic_import(
    "mpfb.ui.apply_assets.useexpression.operators.clearexpression",
    "MPFB_OT_Clear_Expression_Operator",
)


def _fabricate_ex_shape_keys(basemesh, names):
    if not basemesh.data.shape_keys or "Basis" not in basemesh.data.shape_keys.key_blocks:
        TargetService.create_shape_key(basemesh, "Basis", also_create_basis=False)
    for name in names:
        sk_name = TargetService.expression_name_to_shapekey_name(name)
        if sk_name not in basemesh.data.shape_keys.key_blocks:
            TargetService.create_shape_key(basemesh, sk_name, also_create_basis=False)
        basemesh.data.shape_keys.key_blocks[sk_name].value = 0.0


def _write_expression_file(directory, basename, face_units):
    os.makedirs(str(directory), exist_ok=True)
    full = os.path.join(str(directory), basename)
    payload = {
        "format_version": 1,
        "name": os.path.splitext(basename)[0],
        "description": "",
        "tags": [],
        "face_units": face_units,
        "author": "",
        "copyright": "",
        "license": "",
        "homepage": "",
    }
    with open(full, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    return full


def _make_basemesh_active(face_units):
    ObjectService.deselect_and_deactivate_all()
    basemesh = HumanService.create_human()
    _fabricate_ex_shape_keys(basemesh, face_units)
    bpy.context.view_layer.objects.active = basemesh
    # Auto-refit triggers HumanService.refit, which is fine on a freshly-created human but
    # offers nothing to test in this file. Turn it off so we exercise just the operator's
    # core behaviour.
    UseExpressionProperties = dynamic_import(
        "mpfb.ui.apply_assets.useexpression", "UseExpressionProperties"
    )
    UseExpressionProperties.set_value("auto_refit", False, entity_reference=bpy.context.scene)
    return basemesh


def test_operators_exist():
    """The four use-expression operators are registered with bpy.ops."""
    assert bpy.ops.mpfb.apply_expression is not None
    assert bpy.ops.mpfb.set_expression_weight is not None
    assert bpy.ops.mpfb.remove_expression is not None
    assert bpy.ops.mpfb.clear_expression is not None


def test_apply_then_edit_then_remove_then_clear(tmp_path, monkeypatch):
    """Full sequence: apply → set_weight → remove → clear, asserting state at each step."""
    expressions_dir = tmp_path / "user" / "expressions"
    smile = _write_expression_file(expressions_dir, "smile.json", {"jawOpen": 0.4, "mouthSmileLeft": 0.6})
    surprise = _write_expression_file(expressions_dir, "surprise.json", {"jawOpen": 0.3, "browInnerUp": 0.5})

    monkeypatch.setattr(AssetService, "get_available_data_roots", lambda: [str(tmp_path / "user")])
    monkeypatch.setattr(FaceService, "is_faceunits01_installed", lambda force_recheck=False: True)

    basemesh = _make_basemesh_active(["jawOpen", "mouthSmileLeft", "browInnerUp"])
    try:
        # --- apply_expression x2 ---
        mockself = MockOperatorBase(filepath=smile, weight=1.0)
        MPFB_OT_Apply_Expression_Operator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_no_errors()

        mockself = MockOperatorBase(filepath=surprise, weight=1.0)
        MPFB_OT_Apply_Expression_Operator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_no_errors()

        stack = json.loads(basemesh["mpfb_applied_expressions"])
        assert [r["asset"] for r in stack] == ["smile.json", "surprise.json"]
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.7)

        # --- set_expression_weight: dial surprise down to 0.5 ---
        mockself = MockOperatorBase(asset="surprise.json", weight=0.5)
        MPFB_OT_Set_Expression_Weight_Operator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_no_errors()

        # smile contributes jawOpen=0.4, surprise now contributes 0.3*0.5=0.15 → sum 0.55
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.55)
        assert basemesh.data.shape_keys.key_blocks["!ex-browInnerUp"].value == approx(0.25)

        # --- remove_expression: drop surprise ---
        mockself = MockOperatorBase(asset="surprise.json")
        MPFB_OT_Remove_Expression_Operator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_no_errors()

        stack = json.loads(basemesh["mpfb_applied_expressions"])
        assert [r["asset"] for r in stack] == ["smile.json"]
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.4)
        assert basemesh.data.shape_keys.key_blocks["!ex-browInnerUp"].value == approx(0.0)

        # --- clear_expression ---
        mockself = MockOperatorBase()
        MPFB_OT_Clear_Expression_Operator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_no_errors()

        assert basemesh["mpfb_applied_expressions"] == "[]"
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.0)
        assert basemesh.data.shape_keys.key_blocks["!ex-mouthSmileLeft"].value == approx(0.0)
    finally:
        ObjectService.delete_object(basemesh)


def test_apply_expression_refuses_without_pack(tmp_path, monkeypatch):
    """The apply operator must refuse cleanly when faceunits01 isn't installed."""
    monkeypatch.setattr(FaceService, "is_faceunits01_installed", lambda force_recheck=False: False)

    basemesh = _make_basemesh_active([])
    try:
        mockself = MockOperatorBase(filepath="anything.json", weight=1.0)
        result = MPFB_OT_Apply_Expression_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'CANCELLED'}
        errors = [r for r in mockself.mock_report.reports if r[0] == 'ERROR']
        assert errors, "Expected an ERROR report when faceunits01 is not installed"
    finally:
        ObjectService.delete_object(basemesh)
