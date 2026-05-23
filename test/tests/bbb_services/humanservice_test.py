import bpy, os, json
import pytest
from bpy.props import FloatProperty
from pytest import approx
from .. import AssetService
from .. import FaceService
from .. import ObjectService
from .. import HumanService
from .. import MaterialService
from .. import LocationService
from .. import RigService
from .. import SystemService
from .. import TargetService
from .. import UiService
from .. import dynamic_import

HUMAN_PRESET_DICT = {
        "clothes": [
            "female_casualsuit01/female_casualsuit01.mhclo"
        ],
        "color_adjustments": {},
        "eyebrows": "eyebrow001/eyebrow001.mhclo",
        "eyelashes": "eyelashes01/eyelashes01.mhclo",
        "eyes": "high-poly/high-poly.mhclo",
        "eyes_material_settings": {},
        "eyes_material_type": "PROCEDURAL_EYES",
        "hair": "long01/long01.mhclo",
        "phenotype": {
            "age": 0.5,
            "cupsize": 0.550000011920929,
            "firmness": 0.550000011920929,
            "gender": 0.0,
            "height": 0.5,
            "muscle": 0.5,
            "proportions": 0.5,
            "race": {
                "african": 0.0,
                "asian": 0.0,
                "caucasian": 1.0
            },
            "weight": 0.5
        },
        "proxy": "",
        "rig": "default",
        "skin_material_settings": {},
        "skin_material_type": "ENHANCED_SSS",
        "skin_mhmat": "middleage_caucasian_female/middleage_caucasian_female.mhmat",
        "targets": [
            {
                "target": "head-age-decr",
                "value": 1.0
            }
        ],
        "teeth": "",
        "tongue": ""
    }


def test_humanservice_exists():
    """HumanService"""
    assert HumanService is not None, "HumanService can be imported"


def test_create_human_defaults():
    """HumanService.create_human() -- defaults"""
    obj = HumanService.create_human()
    assert obj is not None
    assert getattr(obj, 'MPFB_GEN_object_type') == "Basemesh"
    assert getattr(obj, 'MPFB_GEN_scale_factor') == approx(0.1)
    ObjectService.delete_object(obj)


def test_add_mhclo_asset_without_rig():
    """HumanService.add_mhclo_asset() -- without rig"""
    testdata = LocationService.get_mpfb_test("testdata")
    mhclo_file = os.path.join(testdata, "better_socks_low.mhclo")
    assert os.path.exists(mhclo_file)
    basemesh = HumanService.create_human()
    assert basemesh is not None
    clothes = HumanService.add_mhclo_asset(mhclo_file, basemesh, set_up_rigging=False, interpolate_weights=False, import_subrig=False, import_weights=False)
    assert clothes is not None
    assert clothes.parent == basemesh
    ObjectService.delete_object(clothes)
    ObjectService.delete_object(basemesh)


def test_add_mhclo_asset_with_rig():
    """HumanService.add_mhclo_asset() -- with rig"""
    testdata = LocationService.get_mpfb_test("testdata")
    mhclo_file = os.path.join(testdata, "better_socks_low.mhclo")
    assert os.path.exists(mhclo_file)
    basemesh = HumanService.create_human()
    assert basemesh is not None
    rig = HumanService.add_builtin_rig(basemesh, "default")
    assert rig is not None
    clothes = HumanService.add_mhclo_asset(mhclo_file, basemesh, set_up_rigging=True, interpolate_weights=False, import_subrig=False, import_weights=True)
    assert clothes is not None
    assert clothes.parent == rig
    ObjectService.delete_object(clothes)
    ObjectService.delete_object(basemesh)
    ObjectService.delete_object(rig)


def test_add_builtin_rig_standard():
    """HumanService.add_builtin_rig() -- standard rig"""
    basemesh = HumanService.create_human()
    assert basemesh is not None
    rig = HumanService.add_builtin_rig(basemesh, "default")
    assert rig is not None
    assert basemesh.parent == rig
    ObjectService.delete_object(basemesh)
    ObjectService.delete_object(rig)


def test_serialize_v2_skin():
    """HumanService.serialize_to_json_string() -- v2 skin"""
    basemesh = HumanService.create_human()
    assert basemesh is not None
    human_info = HumanService._create_default_human_info_dict()
    assert human_info
    assert human_info["skin_material_type"] == "NONE"
    assert len(human_info["skin_material_settings"].keys()) == 0

    name = ObjectService.random_name()
    MaterialService.create_v2_skin_material(name, basemesh)

    HumanService._populate_human_info_with_skin_info(human_info, basemesh)

    assert human_info["skin_material_type"] == "LAYERED"
    assert len(human_info["skin_material_settings"].keys()) > 0
    assert "color" in human_info["skin_material_settings"]
    assert "DiffuseTextureStrength" in human_info["skin_material_settings"]["color"]

    ObjectService.delete_object(basemesh)


def test_deserialize_from_dict():
    """HumanService.deserialize_from_dict()"""
    name = ObjectService.random_name()

    human_info = HumanService._create_default_human_info_dict()
    human_info["name"] = name

    deser = HumanService.get_default_deserialization_settings()

    basemesh = HumanService.deserialize_from_dict(human_info, deser)
    assert basemesh
    assert basemesh.name == name + ".body"

    ObjectService.delete_object(basemesh)


def test_deserialize_from_mhm():
    """HumanService.deserialize_from_mhm()"""
    deser = HumanService.get_default_deserialization_settings()
    deser["clothes_deep_search"] = False
    deser["bodypart_deep_search"] = False

    testdata = LocationService.get_mpfb_test("testdata")
    mhm_file = os.path.join(testdata, "testchar.mhm")

    assert os.path.exists(mhm_file)

    basemesh = HumanService.deserialize_from_mhm(mhm_file, deser)
    assert basemesh
    assert basemesh.name == "testchar.body"

    ObjectService.delete_object(basemesh)


def test_serialize_to_json_string():
    """HumanService.serialize_to_json_string()"""
    obj = HumanService.create_human()
    assert obj is not None

    name = ObjectService.random_name()
    obj.name = name + ".body"

    jstr = HumanService.serialize_to_json_string(obj)
    assert jstr
    assert "eyebrows" in jstr

    ObjectService.delete_object(obj)


def test_preset_lists():
    """HumanService.get_list_of_human_presets"""
    HumanService.update_list_of_human_presets()  # Mostly to see it does not crash
    presets = HumanService.get_list_of_human_presets()
    assert presets is not None  # It is probably empty though


def test_serialization():
    """HumanService.deserialize_from_json_string()"""
    deserialization_settings = HumanService.get_default_deserialization_settings()
    basemesh = HumanService.deserialize_from_dict(HUMAN_PRESET_DICT, deserialization_settings)
    assert basemesh
    HumanService.refit(basemesh)
    serialization_json = HumanService.serialize_to_json_string(basemesh)
    serilized_dict = json.loads(serialization_json)
    assert serilized_dict["hair"] == HUMAN_PRESET_DICT["hair"]


def _fabricate_ex_shape_keys(basemesh, names):
    """Add ``!ex-<name>`` shape keys to a basemesh without geometric content.

    Mirrors the pattern used in ``faceservice_test._make_basemesh_with_fake_faceunits`` so
    these tests stay pack-independent.
    """
    if not basemesh.data.shape_keys or "Basis" not in basemesh.data.shape_keys.key_blocks:
        TargetService.create_shape_key(basemesh, "Basis", also_create_basis=False)
    for name in names:
        sk_name = TargetService.expression_name_to_shapekey_name(name)
        if sk_name not in basemesh.data.shape_keys.key_blocks:
            TargetService.create_shape_key(basemesh, sk_name, also_create_basis=False)
        basemesh.data.shape_keys.key_blocks[sk_name].value = 0.0


def test_serialize_excludes_ex_from_targets_and_emits_expressions_list():
    """!ex-* shape keys must be excluded from `targets` and listed under `expressions`."""
    basemesh = HumanService.create_human()
    try:
        _fabricate_ex_shape_keys(basemesh, ["jawOpen", "browInnerUp"])
        # Non-zero values to confirm get_target_stack would otherwise include them.
        basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value = 0.4
        basemesh.data.shape_keys.key_blocks["!ex-browInnerUp"].value = 0.6
        basemesh["mpfb_applied_expressions"] = json.dumps([
            {"asset": "surprise.json", "weight": 0.3},
            {"asset": "smile.json", "weight": 0.7},
        ])

        serialized = json.loads(HumanService.serialize_to_json_string(basemesh))
        assert "expressions" in serialized
        # Sorted by asset for deterministic output.
        assert [r["asset"] for r in serialized["expressions"]] == ["smile.json", "surprise.json"]
        assert serialized["expressions"][0]["weight"] == approx(0.7)
        assert serialized["expressions"][1]["weight"] == approx(0.3)

        # No !ex-* entries leak into the targets stack.
        for entry in serialized["targets"]:
            assert not entry["target"].startswith("!ex-"), entry
    finally:
        ObjectService.delete_object(basemesh)


def test_serialize_populate_with_empty_property_yields_empty_list():
    """A basemesh with no applied-expressions property serializes to an empty list."""
    basemesh = HumanService.create_human()
    try:
        # No property set.
        info = {}
        HumanService._populate_human_info_with_expression_info(info, basemesh)
        assert info["expressions"] == []
    finally:
        ObjectService.delete_object(basemesh)


def test_apply_expressions_from_human_info_no_pack_stores_verbatim(monkeypatch):
    """Without faceunits01 installed, the expressions list is stored on the basemesh but no
    shape-key values are written (and no crash)."""
    monkeypatch.setattr(FaceService, "is_faceunits01_installed", lambda force_recheck=False: False)

    basemesh = HumanService.create_human()
    try:
        human_info = {"expressions": [
            {"asset": "b.json", "weight": 0.4},
            {"asset": "a.json", "weight": 0.6},
        ]}
        HumanService._apply_expressions_from_human_info(human_info, basemesh)

        stored = json.loads(basemesh["mpfb_applied_expressions"])
        # Sorted by asset, weights preserved.
        assert [r["asset"] for r in stored] == ["a.json", "b.json"]
        assert stored[0]["weight"] == approx(0.6)
        # No !ex-* shape keys should have been created.
        if basemesh.data.shape_keys and basemesh.data.shape_keys.key_blocks:
            for block in basemesh.data.shape_keys.key_blocks:
                assert not block.name.startswith("!ex-"), block.name
    finally:
        ObjectService.delete_object(basemesh)


def test_apply_expressions_from_human_info_missing_key_is_noop():
    """A preset without an `expressions` key must load without error and not touch the basemesh."""
    basemesh = HumanService.create_human()
    try:
        HumanService._apply_expressions_from_human_info({}, basemesh)
        assert "mpfb_applied_expressions" not in basemesh
    finally:
        ObjectService.delete_object(basemesh)


def test_apply_expressions_from_human_info_with_pack_applies_aggregated(tmp_path, monkeypatch):
    """With faceunits01 stubbed installed and fabricated !ex-* keys present, the aggregated
    values are written via a single clear_expression + set_expression pass."""
    # Build a fake expressions root and write two files.
    expressions_dir = tmp_path / "user" / "expressions"
    os.makedirs(str(expressions_dir), exist_ok=True)

    def _write(name, face_units):
        with open(os.path.join(str(expressions_dir), name), "w", encoding="utf-8") as f:
            json.dump({
                "format_version": 1,
                "name": name,
                "face_units": face_units,
                "description": "",
                "tags": [],
                "author": "",
                "copyright": "",
                "license": "",
                "homepage": "",
            }, f)

    _write("smile.json", {"jawOpen": 0.4, "mouthSmileLeft": 0.6})
    _write("surprise.json", {"jawOpen": 0.3, "browInnerUp": 0.5})

    monkeypatch.setattr(AssetService, "get_available_data_roots", lambda: [str(tmp_path / "user")])
    monkeypatch.setattr(FaceService, "is_faceunits01_installed", lambda force_recheck=False: True)

    basemesh = HumanService.create_human()
    try:
        _fabricate_ex_shape_keys(basemesh, ["jawOpen", "mouthSmileLeft", "browInnerUp"])
        human_info = {"expressions": [
            {"asset": "smile.json", "weight": 1.0},
            {"asset": "surprise.json", "weight": 1.0},
        ]}
        HumanService._apply_expressions_from_human_info(human_info, basemesh)

        # Live values are the aggregate, clamped.
        assert basemesh.data.shape_keys.key_blocks["!ex-jawOpen"].value == approx(0.7)
        assert basemesh.data.shape_keys.key_blocks["!ex-mouthSmileLeft"].value == approx(0.6)
        assert basemesh.data.shape_keys.key_blocks["!ex-browInnerUp"].value == approx(0.5)
        # And the list is stored verbatim, sorted.
        stored = json.loads(basemesh["mpfb_applied_expressions"])
        assert [r["asset"] for r in stored] == ["smile.json", "surprise.json"]
    finally:
        ObjectService.delete_object(basemesh)


def test_apply_expressions_from_human_info_syncs_library_sliders(tmp_path, monkeypatch):
    """After loading a preset, the expressions-library scene sliders must match the loaded stack.

    The library panel registers one slider per discovered .json at addon load. The
    deserialization flow has to push the loaded weights into those scene props (with the
    panel's update callback suppressed) so the UI reflects the loaded character.
    """
    expressions_dir = tmp_path / "user" / "expressions"
    os.makedirs(str(expressions_dir), exist_ok=True)

    def _write(name, face_units):
        with open(os.path.join(str(expressions_dir), name), "w", encoding="utf-8") as f:
            json.dump({
                "format_version": 1,
                "name": name,
                "face_units": face_units,
                "description": "",
                "tags": [],
                "author": "",
                "copyright": "",
                "license": "",
                "homepage": "",
            }, f)

    _write("smile.json", {"jawOpen": 0.4})
    _write("surprise.json", {"browInnerUp": 0.5})

    monkeypatch.setattr(AssetService, "get_available_data_roots", lambda: [str(tmp_path / "user")])
    monkeypatch.setattr(FaceService, "is_faceunits01_installed", lambda force_recheck=False: True)

    expression_prop_map = dynamic_import(
        "mpfb.ui.apply_assets.useexpression", "_EXPRESSION_PROP_MAP"
    )
    make_slider_update = dynamic_import(
        "mpfb.ui.apply_assets.useexpression", "_make_slider_update"
    )

    smile_id = UiService.as_valid_identifier("expr_smile.json")
    surprise_id = UiService.as_valid_identifier("expr_surprise.json")
    stale_id = UiService.as_valid_identifier("expr_stale.json")
    for asset, identifier in [
        ("smile.json", smile_id),
        ("surprise.json", surprise_id),
        ("stale.json", stale_id),
    ]:
        expression_prop_map[identifier] = {"asset": asset, "label": asset, "absolute_path": ""}
        setattr(bpy.types.Scene, identifier, FloatProperty(
            name=asset, default=0.0, min=0.0, max=1.0, update=make_slider_update(identifier),
        ))

    # Pre-set the stale slider non-zero to verify it gets reset to 0 on load.
    setattr(bpy.context.scene, stale_id, 0.42)

    basemesh = HumanService.create_human()
    try:
        _fabricate_ex_shape_keys(basemesh, ["jawOpen", "browInnerUp"])
        human_info = {"expressions": [
            {"asset": "smile.json", "weight": 0.7},
            {"asset": "surprise.json", "weight": 0.3},
        ]}
        HumanService._apply_expressions_from_human_info(human_info, basemesh)

        assert getattr(bpy.context.scene, smile_id) == approx(0.7)
        assert getattr(bpy.context.scene, surprise_id) == approx(0.3)
        # The slider for an asset not present in the loaded stack must be zeroed.
        assert getattr(bpy.context.scene, stale_id) == approx(0.0)
    finally:
        ObjectService.delete_object(basemesh)
        for identifier in [smile_id, surprise_id, stale_id]:
            expression_prop_map.pop(identifier, None)
            if hasattr(bpy.types.Scene, identifier):
                try:
                    delattr(bpy.types.Scene, identifier)
                except (AttributeError, RuntimeError):
                    pass


def _serialize_rig_after_rigify_generate(basemesh, metarig_type):
    """Add `metarig_type` (e.g. 'rigify.human'), generate with meta_rig_action='delete', serialize, return the 'rig' field."""
    HumanObjectProperties = dynamic_import("mpfb.entities.objectproperties", "HumanObjectProperties")
    HumanObjectProperties.set_value("is_human_project", True, entity_reference=basemesh)
    meta_rig = HumanService.add_builtin_rig(basemesh, metarig_type)
    assert meta_rig is not None
    generated = RigService.generate_rigify_rig(meta_rig, meta_rig_action="delete")
    assert generated is not None
    serialized = json.loads(HumanService.serialize_to_json_string(basemesh))
    return serialized.get("rig")


def _cleanup_named_with_relatives(basemesh_name):
    """Remove the named basemesh plus any objects currently parented to it."""
    for obj in list(bpy.data.objects):
        parent = obj.parent
        if parent is not None and parent.name == basemesh_name:
            bpy.data.objects.remove(obj, do_unlink=True)
    if basemesh_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[basemesh_name], do_unlink=True)


def test_serialize_human_with_generated_rigify_human_infers_human():
    """HumanService.serialize_to_json_string() returns 'rigify.human' for a generated rigify rig from rigify.human"""
    if not SystemService.check_for_rigify():
        pytest.skip("Rigify is not enabled in this Blender install")

    basemesh = HumanService.create_human()
    basemesh_name = basemesh.name
    try:
        rig = _serialize_rig_after_rigify_generate(basemesh, "rigify.human")
        assert rig == "rigify.human", f"Expected 'rigify.human', got {rig!r}"
    finally:
        _cleanup_named_with_relatives(basemesh_name)


def test_serialize_human_with_generated_rigify_human_toes_infers_human_toes():
    """HumanService.serialize_to_json_string() returns 'rigify.human_toes' for a generated rigify rig from rigify.human_toes"""
    if not SystemService.check_for_rigify():
        pytest.skip("Rigify is not enabled in this Blender install")

    basemesh = HumanService.create_human()
    basemesh_name = basemesh.name
    try:
        rig = _serialize_rig_after_rigify_generate(basemesh, "rigify.human_toes")
        assert rig == "rigify.human_toes", f"Expected 'rigify.human_toes', got {rig!r}"
    finally:
        _cleanup_named_with_relatives(basemesh_name)
