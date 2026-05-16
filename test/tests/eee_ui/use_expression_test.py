"""Tests for the expressions-library panel.

These tests fabricate `!ex-*` shape keys without geometric content so they run without the
`faceunits01` asset pack, mirroring the pattern in `bbb_services/faceservice_test.py`. The
faceunits01-installed probe is monkey-patched to True so the slider update callback applies
shape keys instead of treating the pack as missing.
"""

import json, os
import bpy
from bpy.props import FloatProperty
from pytest import approx
from .. import AssetService
from .. import FaceService
from .. import HumanService
from .. import ObjectService
from .. import TargetService
from .. import UiService
from .. import dynamic_import

_EXPRESSION_PROP_MAP = dynamic_import("mpfb.ui.apply_assets.useexpression", "_EXPRESSION_PROP_MAP")
_make_slider_update = dynamic_import("mpfb.ui.apply_assets.useexpression", "_make_slider_update")
write_slider_values = dynamic_import("mpfb.ui.apply_assets.useexpression", "write_slider_values")
ExpressionsLibraryProperties = dynamic_import(
    "mpfb.ui.apply_assets.useexpression", "ExpressionsLibraryProperties"
)


def _fabricate_ex_shape_keys(basemesh, names):
    if not basemesh.data.shape_keys or "Basis" not in basemesh.data.shape_keys.key_blocks:
        TargetService.create_shape_key(basemesh, "Basis", also_create_basis=False)
    for name in names:
        sk_name = TargetService.expression_name_to_shapekey_name(name)
        if sk_name not in basemesh.data.shape_keys.key_blocks:
            TargetService.create_shape_key(basemesh, sk_name, also_create_basis=False)
        basemesh.data.shape_keys.key_blocks[sk_name].value = 0.0


def _write_expression_file(directory, basename, face_units, display_name=None):
    os.makedirs(str(directory), exist_ok=True)
    full = os.path.join(str(directory), basename)
    payload = {
        "format_version": 1,
        "name": display_name if display_name is not None else os.path.splitext(basename)[0],
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
    return basemesh


def _register_temp_slider(asset_fragment, label):
    """Inject a slider entry into _EXPRESSION_PROP_MAP and register its scene FloatProperty.

    Returns the scene-prop identifier. Use _unregister_temp_slider to clean up.
    """
    identifier = UiService.as_valid_identifier("expr_" + asset_fragment)
    _EXPRESSION_PROP_MAP[identifier] = {
        "asset": asset_fragment,
        "label": label,
        "absolute_path": "",
    }
    prop = FloatProperty(
        name=label,
        description=label,
        default=0.0,
        min=0.0,
        max=1.0,
        soft_min=0.0,
        soft_max=1.0,
        update=_make_slider_update(identifier),
    )
    setattr(bpy.types.Scene, identifier, prop)
    return identifier


def _unregister_temp_slider(identifier):
    if hasattr(bpy.types.Scene, identifier):
        try:
            delattr(bpy.types.Scene, identifier)
        except (AttributeError, RuntimeError):
            pass
    _EXPRESSION_PROP_MAP.pop(identifier, None)


def test_slider_drag_updates_stack_and_shape_keys(tmp_path, monkeypatch):
    """Setting the slider scene-prop writes to the stack and refreshes the !ex-* shape keys."""
    expressions_dir = tmp_path / "user" / "expressions"
    _write_expression_file(expressions_dir, "smile.json", {"jawOpen": 0.4, "mouthSmileLeft": 0.6})
    _write_expression_file(expressions_dir, "surprise.json", {"jawOpen": 0.3, "browInnerUp": 0.5})

    monkeypatch.setattr(AssetService, "get_available_data_roots", lambda: [str(tmp_path / "user")])
    monkeypatch.setattr(FaceService, "is_faceunits01_installed", lambda force_recheck=False: True)

    ExpressionsLibraryProperties.set_value(
        "auto_refit", False, entity_reference=bpy.context.scene
    )

    smile_id = _register_temp_slider("smile.json", "Smile")
    surprise_id = _register_temp_slider("surprise.json", "Surprise")

    basemesh = _make_basemesh_active(["jawOpen", "mouthSmileLeft", "browInnerUp"])
    try:
        scene = bpy.context.scene

        # Drag the smile slider to 1.0 — stack gains one row, !ex-* values match the file.
        setattr(scene, smile_id, 1.0)
        stack = json.loads(basemesh["mpfb_applied_expressions"])
        assert [r["asset"] for r in stack] == ["smile.json"]
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.4)
        assert basemesh.data.shape_keys.key_blocks["!ex-mouthSmileLeft"].value == approx(0.6)

        # Drag the surprise slider to 0.5 — second row, jawOpen sums (0.4 + 0.15).
        setattr(scene, surprise_id, 0.5)
        stack = json.loads(basemesh["mpfb_applied_expressions"])
        assert sorted(r["asset"] for r in stack) == ["smile.json", "surprise.json"]
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.55)
        assert basemesh.data.shape_keys.key_blocks["!ex-browInnerUp"].value == approx(0.25)

        # Drag the smile slider back to 0 — the row is removed, shape keys reflect just surprise.
        setattr(scene, smile_id, 0.0)
        stack = json.loads(basemesh["mpfb_applied_expressions"])
        assert [r["asset"] for r in stack] == ["surprise.json"]
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.15)
        assert basemesh.data.shape_keys.key_blocks["!ex-mouthSmileLeft"].value == approx(0.0)

        # And finally drop surprise too — stack is empty, all !ex-* zeroed.
        setattr(scene, surprise_id, 0.0)
        assert basemesh["mpfb_applied_expressions"] == "[]"
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.0)
        assert basemesh.data.shape_keys.key_blocks["!ex-browInnerUp"].value == approx(0.0)
    finally:
        ObjectService.delete_object(basemesh)
        _unregister_temp_slider(smile_id)
        _unregister_temp_slider(surprise_id)


def test_write_slider_values_syncs_props_without_firing_callbacks(tmp_path, monkeypatch):
    """write_slider_values writes weights into the registered scene props with updates suppressed."""
    expressions_dir = tmp_path / "user" / "expressions"
    _write_expression_file(expressions_dir, "smile.json", {"jawOpen": 0.4})

    monkeypatch.setattr(AssetService, "get_available_data_roots", lambda: [str(tmp_path / "user")])
    monkeypatch.setattr(FaceService, "is_faceunits01_installed", lambda force_recheck=False: True)

    smile_id = _register_temp_slider("smile.json", "Smile")

    basemesh = _make_basemesh_active(["jawOpen"])
    try:
        scene = bpy.context.scene
        # Pre-condition: nothing stored.
        assert basemesh.get("mpfb_applied_expressions", None) is None
        # Write a loaded stack into the sliders. The update callback would normally mutate
        # the stack, but write_slider_values suppresses callbacks, so the stack stays empty.
        write_slider_values(scene, [{"asset": "smile.json", "weight": 0.7}])
        assert getattr(scene, smile_id) == approx(0.7)
        assert basemesh.get("mpfb_applied_expressions", None) is None
    finally:
        ObjectService.delete_object(basemesh)
        _unregister_temp_slider(smile_id)
