import bpy
from pytest import approx
from .. import AssetService
from .. import ObjectService
from .. import TargetService
from .. import dynamic_import
from ._helpers import MockOperatorBase

MPFB_OT_Create_Random_Human_Operator = dynamic_import("mpfb.ui.new_human.randomize.operators.createrandomhuman", "MPFB_OT_Create_Random_Human_Operator")
RANDOMIZE_PROPERTIES = dynamic_import("mpfb.ui.new_human.randomize.randomizeproperties", "RANDOMIZE_PROPERTIES")
HumanObjectProperties = dynamic_import("mpfb.entities.objectproperties", "HumanObjectProperties")

# The system skins ship as installed assets; the skin tests only run when some are present.
_SKINS_AVAILABLE = len(AssetService.list_mhmat_assets("skins")) > 0
# Body part meshes are not bundled with MPFB, so the bodypart tests are gated on availability.
_HAIR_AVAILABLE = len(AssetService.list_mhclo_assets("hair")) > 0
_EYES_AVAILABLE = AssetService.find_asset_absolute_path("low-poly/low-poly.mhclo", "eyes") is not None

_PLAIN_BODYPART_ENABLES = ["eyebrows_enable", "eyelashes_enable", "teeth_enable", "tongue_enable"]


def _set_props(**values):
    for name, value in values.items():
        RANDOMIZE_PROPERTIES.set_value(name, value, entity_reference=bpy.context.scene)


# Backwards-compatible alias used by the skin tests below.
_set_skin_props = _set_props


def _disable_bodyparts_and_rig():
    """Turn off the rig and every body part, so the operator produces just a basemesh (plus,
    if skin is on, a skin material). Skin is left untouched so the skin tests control it."""
    _set_props(rig="NONE", eyes_mode="DONOTADD", hair_randomize=False)
    for name in _PLAIN_BODYPART_ENABLES:
        _set_props(**{name: False})


def _find_basemesh():
    """Find the basemesh in the current scene, regardless of which object is active (adding a
    rig makes the armature the active object)."""
    for obj in bpy.context.scene.objects:
        if ObjectService.object_is_basemesh(obj):
            return obj
    return None


def _delete_human():
    """Delete the created basemesh together with all its relatives (rig and body parts)."""
    basemesh = _find_basemesh()
    if basemesh is None:
        return
    for relative in list(ObjectService.find_related_objects(basemesh)):
        if relative is not basemesh:
            ObjectService.delete_object(relative)
    ObjectService.delete_object(basemesh)


def _flatten_macro(macro):
    """Flatten a macro info dict (including the nested race weights) to a plain name -> value dict."""
    flat = {}
    for key, value in macro.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                flat[key + "." + subkey] = subvalue
        else:
            flat[key] = value
    return flat


def _run(seed):
    """Run the operator with a given seed and return the mock operator (for report asserts)."""
    RANDOMIZE_PROPERTIES.set_value("seed", seed, entity_reference=bpy.context.scene)
    ObjectService.deselect_and_deactivate_all()
    mockself = MockOperatorBase()
    MPFB_OT_Create_Random_Human_Operator.hardened_execute(mockself, bpy.context)
    return mockself


def _create_and_read(seed):
    # The phenotype tests only care about the macro, so the rig and body parts are turned off.
    _disable_bodyparts_and_rig()
    mockself = _run(seed)
    mockself.mock_report.assert_no_errors()
    basemesh = _find_basemesh()
    assert basemesh is not None
    assert ObjectService.object_is_basemesh(basemesh)
    macro = TargetService.get_macro_info_dict_from_basemesh(basemesh)
    _delete_human()
    return macro


def _create_and_keep(seed):
    """Create a random human (rig and body parts off) and return (mockself, basemesh)."""
    _disable_bodyparts_and_rig()
    mockself = _run(seed)
    return mockself, _find_basemesh()


def _restore_skin_defaults():
    _set_skin_props(randomize_skin=True, match_gender=True, match_age=True, match_race=True,
                    skin_fallback=True, skin_pack="", skin_include="", skin_exclude="special_suit")
    RANDOMIZE_PROPERTIES.set_value("seed", 0, entity_reference=bpy.context.scene)


def test_operator_exists():
    assert bpy.ops.mpfb.create_random_human is not None


def test_create_random_human_defaults():
    try:
        mockself = _run(0)
        mockself.mock_report.assert_no_errors()
        assert _find_basemesh() is not None
    finally:
        _disable_bodyparts_and_rig()
        _delete_human()
        RANDOMIZE_PROPERTIES.set_value("seed", 0, entity_reference=bpy.context.scene)


def test_same_seed_produces_identical_human():
    try:
        first = _flatten_macro(_create_and_read(4242))
        second = _flatten_macro(_create_and_read(4242))
        assert first.keys() == second.keys()
        for key in first:
            assert first[key] == approx(second[key], abs=1e-4), "Attribute " + key + " differs between identical seeds"
    finally:
        RANDOMIZE_PROPERTIES.set_value("seed", 0, entity_reference=bpy.context.scene)


def test_skin_pick_does_not_shift_phenotype():
    # The skin is drawn after the phenotype, so the phenotype produced by a given seed must
    # be identical whether skin randomization is on or off.
    try:
        _set_skin_props(randomize_skin=True)
        with_skin = _flatten_macro(_create_and_read(31337))
        _set_skin_props(randomize_skin=False)
        without_skin = _flatten_macro(_create_and_read(31337))
        assert with_skin.keys() == without_skin.keys()
        for key in with_skin:
            assert with_skin[key] == approx(without_skin[key], abs=1e-4), "Attribute " + key + " shifted"
    finally:
        _restore_skin_defaults()


def test_skin_disabled_applies_no_material():
    try:
        _set_skin_props(randomize_skin=False)
        _, basemesh = _create_and_keep(123)
        source = HumanObjectProperties.get_value("material_source", entity_reference=basemesh)
        assert not source, "No skin material_source is set when skin randomization is off"
        _delete_human()
    finally:
        _restore_skin_defaults()


def test_skin_enabled_applies_material():
    if not _SKINS_AVAILABLE:
        return
    try:
        _set_skin_props(randomize_skin=True, match_gender=False, match_age=False, match_race=False,
                        skin_pack="", skin_include="", skin_exclude="")
        mockself, basemesh = _create_and_keep(555)
        mockself.mock_report.assert_no_errors()
        source = HumanObjectProperties.get_value("material_source", entity_reference=basemesh)
        assert source, "A skin material_source is set when a skin is applied"
        assert str(source).lower().endswith(".mhmat")
        _delete_human()
    finally:
        _restore_skin_defaults()


def test_skin_same_seed_applies_same_skin():
    if not _SKINS_AVAILABLE:
        return
    try:
        _set_skin_props(randomize_skin=True, match_gender=False, match_age=False, match_race=False,
                        skin_pack="", skin_include="", skin_exclude="")
        _, first = _create_and_keep(4321)
        first_source = HumanObjectProperties.get_value("material_source", entity_reference=first)
        _delete_human()
        _, second = _create_and_keep(4321)
        second_source = HumanObjectProperties.get_value("material_source", entity_reference=second)
        _delete_human()
        assert first_source and first_source == second_source, "The same seed picks the same skin"
    finally:
        _restore_skin_defaults()


def test_skin_no_match_reports_warning():
    if not _SKINS_AVAILABLE:
        return
    try:
        _set_skin_props(randomize_skin=True, match_gender=False, match_age=False, match_race=False,
                        skin_fallback=False, skin_pack="", skin_exclude="",
                        skin_include="definitely_not_a_real_skin_keyword_xyz")
        mockself, basemesh = _create_and_keep(9)
        mockself.mock_report.assert_no_errors()
        mockself.mock_report.assert_reported('WARNING', "No matching skin")
        source = HumanObjectProperties.get_value("material_source", entity_reference=basemesh)
        assert not source, "No skin is applied when nothing matches"
        _delete_human()
    finally:
        _restore_skin_defaults()


def test_default_settings_respect_bounds():
    try:
        macro = _create_and_read(777)
        # With the default spec the scalar attributes are drawn around neutral 0.5 with a
        # 0.5 deviation, so they span the full 0.0-1.0 range. A small tolerance is added for
        # shape-key read-back rounding.
        for name in ["muscle", "weight", "height", "proportions"]:
            assert macro[name] >= 0.0 - 1e-3
            assert macro[name] <= 1.0 + 1e-3
        # Gender is discrete by default, so it is either fully female or fully male.
        assert macro["gender"] == approx(0.0, abs=1e-3) or macro["gender"] == approx(1.0, abs=1e-3)
        # Race weights are normalized to sum to ~1.
        race_sum = macro["race"]["asian"] + macro["race"]["caucasian"] + macro["race"]["african"]
        assert race_sum == approx(1.0, abs=1e-3)
    finally:
        RANDOMIZE_PROPERTIES.set_value("seed", 0, entity_reference=bpy.context.scene)


# --- Body parts and rig -----------------------------------------------------------------


def _disable_all_assets():
    _set_props(randomize_skin=False)
    _disable_bodyparts_and_rig()


def _restore_all_defaults():
    _restore_skin_defaults()
    _set_props(rig="default", eyes_mode="LOWPOLY", hair_randomize=True)
    for name in _PLAIN_BODYPART_ENABLES:
        _set_props(**{name: True})


def test_no_assets_and_no_rig_creates_only_basemesh():
    try:
        _disable_all_assets()
        mockself = _run(111)
        mockself.mock_report.assert_no_errors()
        basemesh = _find_basemesh()
        assert basemesh is not None
        # No rig and no child meshes should have been created.
        assert ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton") is None
        assert len(list(ObjectService.find_related_mesh_assets(basemesh))) == 0
        source = HumanObjectProperties.get_value("material_source", entity_reference=basemesh)
        assert not source, "No skin is applied when skin randomization is off"
        _delete_human()
    finally:
        _restore_all_defaults()


def test_builtin_rig_is_added():
    # The built-in rigs ship with MPFB, so this does not depend on external assets.
    try:
        _disable_all_assets()
        _set_props(rig="default")
        mockself = _run(222)
        mockself.mock_report.assert_no_errors()
        basemesh = _find_basemesh()
        assert basemesh is not None
        assert ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton") is not None, \
            "A Skeleton is created when a rig is chosen"
        _delete_human()
    finally:
        _restore_all_defaults()


def test_bodyparts_are_attached_and_rigged():
    if not (_HAIR_AVAILABLE and _EYES_AVAILABLE):
        return
    try:
        _disable_all_assets()
        # Attach eyes and hair, with a rig so the child meshes are rigged as they attach.
        _set_props(rig="default", eyes_mode="LOWPOLY", hair_randomize=True,
                   hair_match_gender=False, hair_pack="", hair_include="", hair_exclude="",
                   eyes_randomize_alt_materials=False, hair_randomize_alt_materials=False)
        mockself = _run(333)
        mockself.mock_report.assert_no_errors()
        basemesh = _find_basemesh()
        assert basemesh is not None
        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton")
        assert rig is not None, "A Skeleton was created"
        assets = list(ObjectService.find_related_mesh_assets(basemesh))
        assert len(assets) >= 2, "The eyes and hair child meshes were attached"
        # A rigged child mesh is parented to the armature rather than to the basemesh.
        for asset in assets:
            assert asset.parent is rig, "Body part " + asset.name + " is rigged to the skeleton"
        _delete_human()
    finally:
        _restore_all_defaults()


def test_same_seed_attaches_same_hair():
    if not _HAIR_AVAILABLE:
        return
    try:
        _disable_all_assets()
        _set_props(hair_randomize=True, hair_match_gender=False, hair_pack="",
                   hair_include="", hair_exclude="", hair_randomize_alt_materials=False)
        _run(4321)
        first = sorted(a.name for a in ObjectService.find_related_mesh_assets(_find_basemesh()))
        _delete_human()
        _run(4321)
        second = sorted(a.name for a in ObjectService.find_related_mesh_assets(_find_basemesh()))
        _delete_human()
        assert first and first == second, "The same seed attaches the same hair"
    finally:
        _restore_all_defaults()
