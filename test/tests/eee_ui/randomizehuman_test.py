import os
import bpy
import pytest
from pytest import approx
from .. import AssetService
from .. import ObjectService
from .. import TargetService
from .. import dynamic_import
from ._helpers import MockOperatorBase

MPFB_OT_Create_Random_Human_Operator = dynamic_import("mpfb.ui.new_human.randomize.operators.createrandomhuman", "MPFB_OT_Create_Random_Human_Operator")
RANDOMIZE_PROPERTIES = dynamic_import("mpfb.ui.new_human.randomize.randomizeproperties", "RANDOMIZE_PROPERTIES")
DETAIL_SECTIONS = dynamic_import("mpfb.ui.new_human.randomize.randomizeproperties", "DETAIL_SECTIONS")
scene_to_spec = dynamic_import("mpfb.ui.new_human.randomize.randomizeproperties", "scene_to_spec")
spec_to_scene = dynamic_import("mpfb.ui.new_human.randomize.randomizeproperties", "spec_to_scene")
MpfbContext = dynamic_import("mpfb.ui.mpfbcontext", "MpfbContext")
ContextResolveEffort = dynamic_import("mpfb.ui.mpfbcontext", "ContextResolveEffort")
HumanObjectProperties = dynamic_import("mpfb.entities.objectproperties", "HumanObjectProperties")

# The system skins ship as installed assets; the skin tests only run when some are present.
_SKINS_AVAILABLE = len(AssetService.list_mhmat_assets("skins")) > 0
# Body part meshes are not bundled with MPFB, so the bodypart tests are gated on availability.
_HAIR_AVAILABLE = len(AssetService.list_mhclo_assets("hair")) > 0
_EYES_AVAILABLE = AssetService.find_asset_absolute_path("low-poly/low-poly.mhclo", "eyes") is not None
# Clothes are not bundled with MPFB either, so the clothes test is gated on availability.
_CLOTHES_AVAILABLE = len(AssetService.list_mhclo_assets("clothes")) > 0

_PLAIN_BODYPART_ENABLES = ["eyebrows_enable", "eyelashes_enable", "teeth_enable", "tongue_enable"]

# The clothes slots, enabled by default for full body / upper body / lower body / feet. The
# tests disable every slot and re-enable only what they exercise.
_CLOTHES_SLOTS = ["head", "full_body", "upper_body", "lower_body", "hands", "feet", "underwear", "accessories"]
_CLOTHES_DEFAULT_ENABLED = ["full_body", "upper_body", "lower_body", "feet"]


def _set_props(**values):
    for name, value in values.items():
        RANDOMIZE_PROPERTIES.set_value(name, value, entity_reference=bpy.context.scene)


# Backwards-compatible alias used by the skin tests below.
_set_skin_props = _set_props


def _disable_clothes():
    """Turn off every clothes slot, so the operator attaches no garments."""
    for slot in _CLOTHES_SLOTS:
        _set_props(**{"clothes_" + slot + "_enable": False})


def _disable_details():
    """Turn off detail randomization, so the operator applies no detail shape targets."""
    _set_props(randomize_details=False)


def _disable_all_detail_sections():
    """Disable every detail section (min=max=0), so only the sections a test re-enables draw."""
    for section in DETAIL_SECTIONS:
        _set_props(**{"detail_" + section + "_min": 0, "detail_" + section + "_max": 0})


def _disable_bodyparts_and_rig():
    """Turn off the rig and every body part (and all clothes and details), so the operator produces
    just a basemesh (plus, if skin is on, a skin material). Skin is left untouched so the skin tests
    control it."""
    _set_props(add_rig="NONE", eyes_mode="DONOTADD", hair_randomize=False)
    for name in _PLAIN_BODYPART_ENABLES:
        _set_props(**{name: False})
    _disable_clothes()
    _disable_details()


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


def _delete_all_humans():
    """Delete every basemesh in the scene together with its relatives.

    These tests share one Blender session with every other test module, and _find_basemesh()
    returns the first basemesh in the scene. A human left behind by an earlier test or module
    (this module's helpers assume the human they just created is the only one) would otherwise be
    picked up here and read instead of the freshly created one. Clearing them keeps the module
    independent of scene state it did not create."""
    guard = 0
    while guard < 1000 and _find_basemesh() is not None:
        _delete_human()
        guard += 1


@pytest.fixture(autouse=True)
def _isolate_scene():
    """Start and end every test in this module with a scene free of basemeshes."""
    _delete_all_humans()
    yield
    _delete_all_humans()


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
    _set_props(add_rig="default", eyes_mode="LOWPOLY", hair_randomize=True)
    for name in _PLAIN_BODYPART_ENABLES:
        _set_props(**{name: True})
    for slot in _CLOTHES_SLOTS:
        _set_props(**{"clothes_" + slot + "_enable": slot in _CLOTHES_DEFAULT_ENABLED})
    _set_props(randomize_details=True)


def _shape_key_names(basemesh):
    """The set of shape-key names on a basemesh (empty when it has none)."""
    keys = basemesh.data.shape_keys
    if keys is None or keys.key_blocks is None:
        return set()
    return {block.name for block in keys.key_blocks}


def _shape_key_values(basemesh):
    """A name -> value dict of the basemesh's shape keys."""
    keys = basemesh.data.shape_keys
    if keys is None or keys.key_blocks is None:
        return {}
    return {block.name: round(block.value, 5) for block in keys.key_blocks}


def test_details_master_off_ignores_section_settings():
    # With the master toggle off, the section settings must have no effect at all, so the basemesh
    # matches exactly what it produced before this sub-feature existed.
    try:
        _disable_all_assets()
        _set_props(randomize_details=False)
        _disable_all_detail_sections()
        _set_props(detail_nose_min=5, detail_nose_max=5)
        mockself = _run(4321)
        mockself.mock_report.assert_no_errors()
        off_configured = _shape_key_names(_find_basemesh())
        _delete_human()
        _set_props(detail_nose_min=0, detail_nose_max=0)
        _run(4321)
        off_zero = _shape_key_names(_find_basemesh())
        _delete_human()
        assert off_configured == off_zero, "with detail randomization off, the section settings have no effect"
    finally:
        _restore_all_defaults()


def test_details_enabled_adds_shape_keys():
    try:
        _disable_all_assets()
        # Baseline: details off produces just the macro shape keys.
        _set_props(randomize_details=False)
        _run(4321)
        baseline = _shape_key_names(_find_basemesh())
        _delete_human()
        # Details on, with a single section drawing a fixed number of categories.
        _set_props(randomize_details=True)
        _disable_all_detail_sections()
        _set_props(detail_nose_min=3, detail_nose_max=3)
        mockself = _run(4321)
        mockself.mock_report.assert_no_errors()
        with_details = _shape_key_names(_find_basemesh())
        assert baseline <= with_details, "the macro shape keys are unchanged by detail randomization"
        assert len(with_details) > len(baseline), "detail randomization adds shape keys to the basemesh"
        assert any(name.startswith("nose-") for name in with_details - baseline), "the extra shape keys are nose detail targets"
        _delete_human()
    finally:
        _restore_all_defaults()


def test_details_same_seed_produces_same_shape_keys():
    try:
        _disable_all_assets()
        _set_props(randomize_details=True)
        _disable_all_detail_sections()
        _set_props(detail_nose_min=2, detail_nose_max=4, detail_head_min=1, detail_head_max=2)
        _run(2024)
        first = _shape_key_values(_find_basemesh())
        _delete_human()
        _run(2024)
        second = _shape_key_values(_find_basemesh())
        _delete_human()
        assert first == second, "the same seed produces the same detail shape keys and values"
    finally:
        _restore_all_defaults()


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
        _set_props(add_rig="default")
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
        _set_props(add_rig="default", eyes_mode="LOWPOLY", hair_randomize=True,
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


# --- Clothes ----------------------------------------------------------------------------


def _enable_only_clothes_slot(slot, **overrides):
    """Disable every clothes slot, then enable one slot with the given filter overrides."""
    _disable_clothes()
    props = {"clothes_" + slot + "_enable": True, "clothes_" + slot + "_chance": 100,
             "clothes_" + slot + "_include_female": "", "clothes_" + slot + "_include_male": "",
             "clothes_" + slot + "_pack": "", "clothes_" + slot + "_exclude": ""}
    for name, value in overrides.items():
        props["clothes_" + slot + "_" + name] = value
    _set_props(**props)


def test_clothes_are_attached_and_rigged():
    if not _CLOTHES_AVAILABLE:
        return
    try:
        _disable_all_assets()
        # Map one slot onto a specific installed garment by its full name, so the pool is not
        # empty regardless of which clothes happen to be installed.
        first_name = os.path.splitext(os.path.basename(str(AssetService.list_mhclo_assets("clothes")[0])))[0]
        _set_props(add_rig="default", asset_material_type="MAKESKIN")
        _enable_only_clothes_slot("head", include_any=first_name)
        mockself = _run(555)
        mockself.mock_report.assert_no_errors()
        basemesh = _find_basemesh()
        assert basemesh is not None
        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton")
        assert rig is not None, "A Skeleton was created"
        assets = list(ObjectService.find_related_mesh_assets(basemesh))
        assert len(assets) >= 1, "A garment was attached"
        # A rigged garment is parented to the armature rather than to the basemesh.
        for asset in assets:
            assert asset.parent is rig, "Garment " + asset.name + " is rigged to the skeleton"
        _delete_human()
    finally:
        _restore_all_defaults()


def test_disabled_clothes_attach_nothing():
    if not _CLOTHES_AVAILABLE:
        return
    try:
        _disable_all_assets()
        _set_props(add_rig="default")
        mockself = _run(556)
        mockself.mock_report.assert_no_errors()
        basemesh = _find_basemesh()
        assert basemesh is not None
        assert len(list(ObjectService.find_related_mesh_assets(basemesh))) == 0, \
            "No garments are attached when every clothes slot is disabled"
        _delete_human()
    finally:
        _restore_all_defaults()


def test_same_seed_attaches_same_clothes():
    if not _CLOTHES_AVAILABLE:
        return
    try:
        _disable_all_assets()
        first_name = os.path.splitext(os.path.basename(str(AssetService.list_mhclo_assets("clothes")[0])))[0]
        _enable_only_clothes_slot("head", include_any=first_name)
        _run(4322)
        first = sorted(a.name for a in ObjectService.find_related_mesh_assets(_find_basemesh()))
        _delete_human()
        _run(4322)
        second = sorted(a.name for a in ObjectService.find_related_mesh_assets(_find_basemesh()))
        _delete_human()
        assert first and first == second, "The same seed attaches the same clothes"
    finally:
        _restore_all_defaults()


def test_mpfbcontext_accepts_randomize_properties():
    # The preset operators build a MpfbContext from RANDOMIZE_PROPERTIES. Property names which
    # collide with the attributes MpfbContext always sets on itself (such as "rig") make this
    # raise a duplicate key error, so this guards against future reserved-name collisions.
    ctx = MpfbContext(context=bpy.context, scene_properties=RANDOMIZE_PROPERTIES, effort=ContextResolveEffort.NONE)
    assert hasattr(ctx, "add_rig")
    assert hasattr(ctx, "available_presets")


def test_preset_spec_roundtrip_keeps_rig():
    try:
        _set_props(add_rig="default")
        spec = scene_to_spec(bpy.context.scene)
        assert spec["creation"]["rig"] == "default"
        _set_props(add_rig="NONE")
        spec_to_scene(spec, bpy.context.scene)
        assert RANDOMIZE_PROPERTIES.get_value("add_rig", entity_reference=bpy.context.scene) == "default"
    finally:
        _restore_all_defaults()


def test_preset_with_unavailable_rig_falls_back_to_none():
    # A preset can refer to a custom rig which has since been uninstalled. Loading it must fall
    # back to "No rig" rather than raise when assigning an unknown identifier to the enum.
    try:
        spec = scene_to_spec(bpy.context.scene)
        spec["creation"]["rig"] = "custom.does_not_exist"
        spec_to_scene(spec, bpy.context.scene)
        assert RANDOMIZE_PROPERTIES.get_value("add_rig", entity_reference=bpy.context.scene) == "NONE"
    finally:
        _restore_all_defaults()
