import bpy, os, json, tempfile
from pytest import approx
from .. import AssetService
from .. import FaceService
from .. import HumanService
from .. import LocationService
from .. import ObjectService
from .. import TargetService
from .. import dynamic_import


# ARKit names used in the fabricated-shape-key tests below. We pick a small subset that covers
# multiple regions so we can exercise additivity, partial-clear, and round-trip behaviour without
# fabricating all 52 shape keys per test.
_TEST_FACE_UNITS = ["browDownLeft", "cheekPuff", "jawOpen", "mouthSmileLeft"]


def _make_basemesh_with_fake_faceunits(face_units=None):
    """Create a basemesh and fabricate `!ex-<name>` shape keys for the given face units.

    This is intentionally pack-independent: the fabricated shape keys have no displacement, but
    `set_expression`/`clear_expression`/`read_current_expression` only manipulate
    `key_blocks[name].value` so they don't care about geometric content. Tests that exercise the
    on-demand load_target path are gated on `FaceService.is_faceunits01_installed()` instead.
    """
    if face_units is None:
        face_units = list(_TEST_FACE_UNITS)
    basemesh = HumanService.create_human()
    assert basemesh is not None
    if not basemesh.data.shape_keys or "Basis" not in basemesh.data.shape_keys.key_blocks:
        TargetService.create_shape_key(basemesh, "Basis", also_create_basis=False)
    for face_unit_name in face_units:
        sk_name = TargetService.expression_name_to_shapekey_name(face_unit_name)
        if sk_name not in basemesh.data.shape_keys.key_blocks:
            TargetService.create_shape_key(basemesh, sk_name, also_create_basis=False)
        basemesh.data.shape_keys.key_blocks[sk_name].value = 0.0
    return basemesh


def test_faceservice_exists():
    """FaceService"""
    assert FaceService is not None, "FaceService can be imported"


def test_arkit_faceunits_has_52_entries():
    """ARKIT_FACEUNITS has exactly 52 face units (the canonical ARKit set)."""
    arkit = dynamic_import("mpfb.services.faceservice", "ARKIT_FACEUNITS")
    assert len(arkit) == 52


def test_faceunit_regions_cover_all_arkit_units():
    """FACEUNIT_REGIONS partitions ARKIT_FACEUNITS — every name appears in exactly one region."""
    arkit = dynamic_import("mpfb.services.faceservice", "ARKIT_FACEUNITS")
    regions = dynamic_import("mpfb.services.faceservice", "FACEUNIT_REGIONS")

    seen = []
    for region_name, names in regions.items():
        for name in names:
            assert name in arkit, f"{name} (in region {region_name}) is not a known ARKit face unit"
            assert name not in seen, f"{name} appears in more than one region"
            seen.append(name)
    assert sorted(seen) == sorted(arkit), "Some ARKit face units are not assigned to any region"


def test_faceunit_descriptions_cover_all_units():
    """FACEUNIT_DESCRIPTIONS provides a non-empty description for every ARKit face unit."""
    arkit = dynamic_import("mpfb.services.faceservice", "ARKIT_FACEUNITS")
    descriptions = dynamic_import("mpfb.services.faceservice", "FACEUNIT_DESCRIPTIONS")
    for name in arkit:
        assert name in descriptions, f"No description for {name}"
        assert descriptions[name].strip(), f"Empty description for {name}"


def test_is_faceunits01_installed_returns_bool():
    """is_faceunits01_installed() returns a bool regardless of whether the pack is installed."""
    result = FaceService.is_faceunits01_installed()
    assert isinstance(result, bool)
    # And should be cached — second call returns the same value.
    assert FaceService.is_faceunits01_installed() == result


def test_set_expression_writes_shape_key_values():
    """set_expression() writes the matching `!ex-<name>` shape key value."""
    basemesh = _make_basemesh_with_fake_faceunits()
    try:
        FaceService.set_expression(basemesh, {"jawOpen": 0.7})
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.7)
    finally:
        ObjectService.delete_object(basemesh)


def test_set_expression_is_additive():
    """set_expression() is additive — values not in the dict are not changed."""
    basemesh = _make_basemesh_with_fake_faceunits()
    try:
        FaceService.set_expression(basemesh, {"jawOpen": 0.7})
        FaceService.set_expression(basemesh, {"cheekPuff": 0.3})
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.7)
        assert basemesh.data.shape_keys.key_blocks["!ex-cheekPuff"].value == approx(0.3)
    finally:
        ObjectService.delete_object(basemesh)


def test_set_expression_warns_on_unknown_key():
    """set_expression() does not raise on unknown ARKit names — it warns and skips."""
    basemesh = _make_basemesh_with_fake_faceunits()
    try:
        # Should not raise.
        FaceService.set_expression(basemesh, {"notAFaceUnit": 0.5, "jawOpen": 0.4})
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.4)
        assert "!ex-notAFaceUnit" not in basemesh.data.shape_keys.key_blocks
    finally:
        ObjectService.delete_object(basemesh)


def test_clear_expression_zeroes_all():
    """clear_expression() zeroes every fabricated `!ex-` shape key."""
    basemesh = _make_basemesh_with_fake_faceunits()
    try:
        for name in _TEST_FACE_UNITS:
            sk = TargetService.expression_name_to_shapekey_name(name)
            basemesh.data.shape_keys.key_blocks[sk].value = 0.5
        FaceService.clear_expression(basemesh)
        for name in _TEST_FACE_UNITS:
            sk = TargetService.expression_name_to_shapekey_name(name)
            assert basemesh.data.shape_keys.key_blocks[sk].value == approx(0.0)
    finally:
        ObjectService.delete_object(basemesh)


def test_clear_expression_does_not_touch_other_shape_keys():
    """clear_expression() only zeroes !ex- keys; macrodetail keys must be untouched."""
    basemesh = _make_basemesh_with_fake_faceunits()
    try:
        # Set one macrodetail-* shape key to a specific value, then confirm clear_expression
        # doesn't change it.
        macro_keys = {}
        for kb in basemesh.data.shape_keys.key_blocks:
            if kb.name.startswith("$md-") or kb.name.startswith("macrodetail-"):
                kb.value = 0.42
                macro_keys[kb.name] = kb.value
                break  # one is enough to prove the point

        FaceService.clear_expression(basemesh)

        for name, value in macro_keys.items():
            assert basemesh.data.shape_keys.key_blocks[name].value == approx(value)
    finally:
        ObjectService.delete_object(basemesh)


def test_read_current_expression_returns_all_52_keys():
    """read_current_expression() returns a dict with all 52 ARKit names — absent ones default to 0.0."""
    basemesh = _make_basemesh_with_fake_faceunits(["jawOpen"])
    try:
        basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value = 0.6
        result = FaceService.read_current_expression(basemesh)
        arkit = dynamic_import("mpfb.services.faceservice", "ARKIT_FACEUNITS")
        assert set(result.keys()) == set(arkit)
        assert result["jawOpen"] == approx(0.6)
        # An ARKit unit whose !ex- shape key was never created reports as 0.0.
        assert result["browInnerUp"] == approx(0.0)
    finally:
        ObjectService.delete_object(basemesh)


def test_save_expression_writes_filtered_json(tmp_path):
    """save_expression() writes JSON with zero values dropped, weights rounded, defaults present."""
    target = str(tmp_path / "smile-test.json")
    expression_dict = {
        "jawOpen": 0.5,
        "browInnerUp": 0.123456789,  # check rounding to 4 decimals
        "cheekPuff": 0.0,            # check zero filtering
        "mouthSmileLeft": 0.3,
    }
    metadata = {"name": "smile-test", "tags": ["happy", "subtle"]}

    FaceService.save_expression(target, expression_dict, metadata)
    assert os.path.exists(target)

    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["format_version"] == 1
    assert data["name"] == "smile-test"
    assert data["face_units"]["jawOpen"] == 0.5
    assert data["face_units"]["browInnerUp"] == 0.1235  # rounded
    assert data["face_units"]["mouthSmileLeft"] == 0.3
    assert "cheekPuff" not in data["face_units"]  # zero filtered out
    assert data["tags"] == ["happy", "subtle"]
    # Defaults for missing optional metadata fields.
    assert data["author"] == ""
    assert data["copyright"] == ""
    assert data["license"] == ""
    assert data["homepage"] == ""
    assert data["description"] == ""


def test_save_expression_accepts_comma_separated_tags(tmp_path):
    """save_expression() splits a comma-separated tag string into a list."""
    target = str(tmp_path / "tags-test.json")
    FaceService.save_expression(
        target,
        {"jawOpen": 0.4},
        {"name": "tags-test", "tags": "happy , subtle, portrait"},
    )
    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["tags"] == ["happy", "subtle", "portrait"]


def test_save_expression_skips_unknown_face_units(tmp_path):
    """save_expression() drops face units not in ARKIT_FACEUNITS."""
    target = str(tmp_path / "unknown-test.json")
    FaceService.save_expression(
        target,
        {"jawOpen": 0.5, "notAFaceUnit": 0.3},
        {"name": "unknown-test"},
    )
    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "jawOpen" in data["face_units"]
    assert "notAFaceUnit" not in data["face_units"]


def test_save_load_round_trip(tmp_path):
    """save_expression() + load_expression() round-trip preserves face units and metadata."""
    target = str(tmp_path / "rt.json")
    expression_dict = {"jawOpen": 0.5, "mouthSmileLeft": 0.3, "browInnerUp": 0.7}
    metadata = {
        "name": "rt",
        "description": "Round trip test",
        "tags": ["a", "b"],
        "author": "Tester",
        "copyright": "(c) 2026",
        "license": "CC0",
        "homepage": "https://example.com",
    }
    FaceService.save_expression(target, expression_dict, metadata)
    loaded_dict, loaded_meta = FaceService.load_expression(target)

    assert loaded_dict == {"jawOpen": 0.5, "mouthSmileLeft": 0.3, "browInnerUp": 0.7}
    assert loaded_meta["name"] == "rt"
    assert loaded_meta["description"] == "Round trip test"
    assert loaded_meta["tags"] == ["a", "b"]
    assert loaded_meta["author"] == "Tester"
    assert loaded_meta["copyright"] == "(c) 2026"
    assert loaded_meta["license"] == "CC0"
    assert loaded_meta["homepage"] == "https://example.com"


def test_load_expression_warns_on_unknown_face_unit(tmp_path):
    """load_expression() skips unknown face_units keys and does not raise."""
    target = str(tmp_path / "with-unknown.json")
    payload = {
        "format_version": 1,
        "name": "with-unknown",
        "face_units": {"jawOpen": 0.4, "notAFaceUnit": 0.5},
    }
    with open(target, "w", encoding="utf-8") as f:
        json.dump(payload, f)

    expression_dict, metadata = FaceService.load_expression(target)
    assert expression_dict == {"jawOpen": 0.4}
    assert metadata["name"] == "with-unknown"


def test_load_expression_tolerates_minimal_document(tmp_path):
    """load_expression() applies empty-string defaults when optional metadata is absent."""
    target = str(tmp_path / "minimal.json")
    payload = {
        "format_version": 1,
        "name": "minimal",
        "face_units": {"jawOpen": 0.2},
    }
    with open(target, "w", encoding="utf-8") as f:
        json.dump(payload, f)

    expression_dict, metadata = FaceService.load_expression(target)
    assert expression_dict == {"jawOpen": 0.2}
    assert metadata["description"] == ""
    assert metadata["tags"] == []
    assert metadata["author"] == ""


def test_load_expression_tolerates_unknown_top_level_keys(tmp_path):
    """load_expression() ignores unknown top-level keys (forward compatibility)."""
    target = str(tmp_path / "future.json")
    payload = {
        "format_version": 2,
        "name": "future",
        "face_units": {"jawOpen": 0.2},
        "future_field": {"foo": "bar"},
    }
    with open(target, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    expression_dict, metadata = FaceService.load_expression(target)
    assert expression_dict == {"jawOpen": 0.2}
    assert metadata["name"] == "future"


def test_save_expression_to_user_data(monkeypatch, tmp_path):
    """save_expression() with a bare name resolves under <user_data>/expressions/ and creates it."""
    fake_user = tmp_path / "userdata"
    fake_user.mkdir()

    # LocationService is a singleton instance. setattr on it shadows the class method without
    # descriptor binding, so the replacement must NOT take a `self` argument.
    def fake_get_user_data(sub_path=None):
        if sub_path:
            return str(fake_user / sub_path)
        return str(fake_user)

    monkeypatch.setattr(LocationService, "get_user_data", fake_get_user_data)

    target_path = FaceService.save_expression(
        "smile-bare",
        {"jawOpen": 0.4},
        {"name": "smile-bare"},
    )

    assert os.path.exists(target_path)
    assert target_path.endswith("smile-bare.json")
    assert os.path.dirname(target_path).endswith("expressions")


def _write_expression_file(directory, basename, face_units, name=None):
    """Helper: write a minimal-but-valid expression JSON file and return its absolute path."""
    os.makedirs(str(directory), exist_ok=True)
    full = os.path.join(str(directory), basename)
    payload = {
        "format_version": 1,
        "name": name or os.path.splitext(basename)[0],
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


def _patch_expressions_root(monkeypatch, expressions_dir):
    """Patch the asset-root scan so only the given expressions/ directory is visible.

    Used by tests that exercise apply_expression_file, aggregate_expression_stack, and
    list_available_expressions without depending on whatever expressions exist on the host's
    real user_data root.
    """
    parent = os.path.dirname(str(expressions_dir))

    def fake_get_available_data_roots():
        return [parent]

    monkeypatch.setattr(AssetService, "get_available_data_roots", fake_get_available_data_roots)


def test_aggregate_expression_stack_sums_with_clamp(tmp_path, monkeypatch):
    """aggregate_expression_stack() sums per face unit across rows and clamps to [0, 1]."""
    expressions_dir = tmp_path / "user" / "expressions"
    _write_expression_file(expressions_dir, "smile.json", {"jawOpen": 0.4, "mouthSmileLeft": 0.6})
    _write_expression_file(expressions_dir, "surprise.json", {"jawOpen": 0.3, "browInnerUp": 0.5})
    _patch_expressions_root(monkeypatch, expressions_dir)

    stack = [
        {"asset": "smile.json", "weight": 1.0},
        {"asset": "surprise.json", "weight": 1.0},
    ]
    aggregated = FaceService.aggregate_expression_stack(stack)
    # jawOpen: 0.4 + 0.3 = 0.7 (within [0,1])
    assert aggregated["jawOpen"] == approx(0.7)
    assert aggregated["mouthSmileLeft"] == approx(0.6)
    assert aggregated["browInnerUp"] == approx(0.5)


def test_aggregate_expression_stack_clamps_at_one(tmp_path, monkeypatch):
    """Three rows whose summed contribution exceeds 1.0 for a face unit are clamped."""
    expressions_dir = tmp_path / "user" / "expressions"
    _write_expression_file(expressions_dir, "a.json", {"jawOpen": 0.6})
    _write_expression_file(expressions_dir, "b.json", {"jawOpen": 0.6})
    _write_expression_file(expressions_dir, "c.json", {"jawOpen": 0.6})
    _patch_expressions_root(monkeypatch, expressions_dir)

    stack = [
        {"asset": "a.json", "weight": 1.0},
        {"asset": "b.json", "weight": 1.0},
        {"asset": "c.json", "weight": 1.0},
    ]
    aggregated = FaceService.aggregate_expression_stack(stack)
    assert aggregated["jawOpen"] == approx(1.0)


def test_aggregate_expression_stack_applies_row_weight(tmp_path, monkeypatch):
    """Each face-unit contribution is loaded_weight * row_weight."""
    expressions_dir = tmp_path / "user" / "expressions"
    _write_expression_file(expressions_dir, "half.json", {"jawOpen": 1.0})
    _patch_expressions_root(monkeypatch, expressions_dir)

    aggregated = FaceService.aggregate_expression_stack([{"asset": "half.json", "weight": 0.25}])
    assert aggregated["jawOpen"] == approx(0.25)


def test_aggregate_expression_stack_skips_missing_files(tmp_path, monkeypatch):
    """A row whose asset cannot be resolved is skipped, others still apply."""
    expressions_dir = tmp_path / "user" / "expressions"
    _write_expression_file(expressions_dir, "real.json", {"jawOpen": 0.4})
    _patch_expressions_root(monkeypatch, expressions_dir)

    stack = [
        {"asset": "real.json", "weight": 1.0},
        {"asset": "nonexistent.json", "weight": 1.0},
    ]
    aggregated = FaceService.aggregate_expression_stack(stack)
    assert aggregated["jawOpen"] == approx(0.4)


def test_apply_expression_file_writes_property_and_shape_keys(tmp_path, monkeypatch):
    """apply_expression_file() writes the stack property and the live !ex- shape keys."""
    expressions_dir = tmp_path / "user" / "expressions"
    smile = _write_expression_file(expressions_dir, "smile.json", {"jawOpen": 0.4, "mouthSmileLeft": 0.6})
    surprise = _write_expression_file(expressions_dir, "surprise.json", {"jawOpen": 0.3, "browInnerUp": 0.5})
    _patch_expressions_root(monkeypatch, expressions_dir)

    basemesh = _make_basemesh_with_fake_faceunits(["jawOpen", "mouthSmileLeft", "browInnerUp"])
    try:
        FaceService.apply_expression_file(basemesh, smile, weight=1.0, append=True)
        FaceService.apply_expression_file(basemesh, surprise, weight=1.0, append=True)

        # Stack property: two rows, sorted by asset.
        raw = basemesh.get("mpfb_applied_expressions", "[]")
        stack = json.loads(raw)
        assert [r["asset"] for r in stack] == ["smile.json", "surprise.json"]
        assert all(r["weight"] == approx(1.0) for r in stack)

        # Live values: summed and clamped.
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.7)
        assert basemesh.data.shape_keys.key_blocks["!ex-mouthSmileLeft"].value == approx(0.6)
        assert basemesh.data.shape_keys.key_blocks["!ex-browInnerUp"].value == approx(0.5)
    finally:
        ObjectService.delete_object(basemesh)


def test_apply_expression_file_latest_wins_dedup(tmp_path, monkeypatch):
    """Applying the same file twice replaces the existing row's weight (latest-wins)."""
    expressions_dir = tmp_path / "user" / "expressions"
    smile = _write_expression_file(expressions_dir, "smile.json", {"jawOpen": 0.5})
    _patch_expressions_root(monkeypatch, expressions_dir)

    basemesh = _make_basemesh_with_fake_faceunits(["jawOpen"])
    try:
        FaceService.apply_expression_file(basemesh, smile, weight=0.5, append=True)
        FaceService.apply_expression_file(basemesh, smile, weight=0.8, append=True)

        stack = json.loads(basemesh.get("mpfb_applied_expressions", "[]"))
        assert len(stack) == 1
        assert stack[0]["asset"] == "smile.json"
        assert stack[0]["weight"] == approx(0.8)
        # Live value: 0.5 * 0.8 = 0.4
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.4)
    finally:
        ObjectService.delete_object(basemesh)


def test_apply_expression_file_replace_mode(tmp_path, monkeypatch):
    """With append=False the stack is replaced by a single row regardless of prior contents."""
    expressions_dir = tmp_path / "user" / "expressions"
    smile = _write_expression_file(expressions_dir, "smile.json", {"jawOpen": 0.4})
    surprise = _write_expression_file(expressions_dir, "surprise.json", {"browInnerUp": 0.5})
    _patch_expressions_root(monkeypatch, expressions_dir)

    basemesh = _make_basemesh_with_fake_faceunits(["jawOpen", "browInnerUp"])
    try:
        FaceService.apply_expression_file(basemesh, smile, weight=1.0, append=True)
        FaceService.apply_expression_file(basemesh, surprise, weight=1.0, append=False)

        stack = json.loads(basemesh.get("mpfb_applied_expressions", "[]"))
        assert [r["asset"] for r in stack] == ["surprise.json"]
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.0)
        assert basemesh.data.shape_keys.key_blocks["!ex-browInnerUp"].value == approx(0.5)
    finally:
        ObjectService.delete_object(basemesh)


def test_clear_applied_expressions_empties_stack_and_values(tmp_path, monkeypatch):
    """clear_applied_expressions() empties the stack and zeroes every !ex- shape key."""
    expressions_dir = tmp_path / "user" / "expressions"
    smile = _write_expression_file(expressions_dir, "smile.json", {"jawOpen": 0.4, "mouthSmileLeft": 0.6})
    _patch_expressions_root(monkeypatch, expressions_dir)

    basemesh = _make_basemesh_with_fake_faceunits(["jawOpen", "mouthSmileLeft"])
    try:
        FaceService.apply_expression_file(basemesh, smile, weight=1.0, append=True)
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.4)

        FaceService.clear_applied_expressions(basemesh)

        assert basemesh.get("mpfb_applied_expressions", "[]") == "[]"
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.0)
        assert basemesh.data.shape_keys.key_blocks["!ex-mouthSmileLeft"].value == approx(0.0)
    finally:
        ObjectService.delete_object(basemesh)


def test_list_available_expressions_user_root_wins(tmp_path, monkeypatch):
    """When the same relative path exists in multiple roots, the higher-priority root wins."""
    # Two roots; we set get_available_data_roots to return [low_priority, high_priority] — the
    # AssetService scan walks them in order, and FaceService.list_available_expressions takes
    # the first occurrence per relative path (so the first root in the list wins).
    high_root = tmp_path / "high"
    low_root = tmp_path / "low"
    _write_expression_file(high_root / "expressions", "smile.json", {"jawOpen": 0.9}, name="high")
    _write_expression_file(low_root / "expressions", "smile.json", {"jawOpen": 0.1}, name="low")

    def fake_get_available_data_roots():
        return [str(high_root), str(low_root)]

    monkeypatch.setattr(AssetService, "get_available_data_roots", fake_get_available_data_roots)

    items = FaceService.list_available_expressions()
    relative_names = [rel for _abs, rel, _meta in items]
    assert relative_names == ["smile.json"]  # de-duplicated
    _abs, _rel, meta = items[0]
    assert meta["name"] == "high"  # higher-priority root wins
