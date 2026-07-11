import bpy
import pytest
from pytest import approx
from .. import ObjectService
from .. import TargetService
from .. import RandomizationService
from .. import dynamic_import
from ._helpers import MockOperatorBase

MPFB_OT_Create_Random_Human_Operator = dynamic_import(
    "mpfb.ui.new_human.randomize.operators.createrandomhuman", "MPFB_OT_Create_Random_Human_Operator")
RANDOMIZE_PROPERTIES = dynamic_import("mpfb.ui.new_human.randomize.randomizeproperties", "RANDOMIZE_PROPERTIES")

_PLAIN_BODYPART_ENABLES = ["eyebrows_enable", "eyelashes_enable", "teeth_enable", "tongue_enable"]
_CLOTHES_SLOTS = ["head", "full_body", "upper_body", "lower_body", "hands", "feet", "underwear", "accessories"]


def _set_props(**values):
    for name, value in values.items():
        RANDOMIZE_PROPERTIES.set_value(name, value, entity_reference=bpy.context.scene)


def _minimal_scene():
    """Turn off the rig and every asset and detail, so each character is just a basemesh.

    This keeps the batch tests fast and free of any dependency on installed assets, so they run
    the same everywhere.
    """
    _set_props(rig="NONE", eyes_mode="DONOTADD", hair_randomize=False, randomize_skin=False,
               randomize_details=False, new_random_seed=False)
    for name in _PLAIN_BODYPART_ENABLES:
        _set_props(**{name: False})
    for slot in _CLOTHES_SLOTS:
        _set_props(**{"clothes_" + slot + "_enable": False})


def _find_basemeshes():
    return [obj for obj in bpy.data.objects if ObjectService.object_is_basemesh(obj)]


def _delete_all_humans():
    """Delete every basemesh in the scene together with its relatives, keeping the module isolated."""
    guard = 0
    while guard < 1000 and _find_basemeshes():
        basemesh = _find_basemeshes()[0]
        for relative in list(ObjectService.find_related_objects(basemesh)):
            if relative is not basemesh:
                ObjectService.delete_object(relative)
        ObjectService.delete_object(basemesh)
        guard += 1


def _delete_batch_collections():
    """Remove any leftover "Random humans" collections so their names do not accumulate."""
    for collection in list(bpy.data.collections):
        if collection.name.startswith("Random humans"):
            bpy.data.collections.remove(collection)


@pytest.fixture(autouse=True)
def _isolate_scene():
    _delete_all_humans()
    _delete_batch_collections()
    yield
    _delete_all_humans()
    _delete_batch_collections()


def _run_batch(base_seed):
    """Run the batch operator synchronously and return the new batch collection.

    The batch operator is driven through bpy.ops (which uses a real operator instance) rather
    than the MockOperatorBase trick, because its synchronous path calls instance methods a mock
    does not have. In background mode bpy.ops uses the EXEC path, i.e. the synchronous loop.
    """
    _set_props(seed=base_seed)
    ObjectService.deselect_and_deactivate_all()
    before = set(bpy.data.collections)
    result = bpy.ops.mpfb.create_random_human_batch()
    assert result == {'FINISHED'}, "the batch operator finished cleanly"
    new_collections = [c for c in bpy.data.collections if c not in before]
    assert len(new_collections) == 1, "the batch created exactly one collection"
    return new_collections[0]


def _flatten_macro(macro):
    flat = {}
    for key, value in macro.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                flat[key + "." + subkey] = subvalue
        else:
            flat[key] = value
    return flat


def test_batch_operator_exists():
    assert bpy.ops.mpfb.create_random_human_batch is not None


def test_batch_creates_count_characters_in_a_collection():
    try:
        _minimal_scene()
        _set_props(batch_count=3, batch_strategy="GRID", batch_random_rotation=False)
        collection = _run_batch(2026)
        assert collection.name.startswith("Random humans"), "the batch collection is named 'Random humans'"
        basemeshes = [obj for obj in collection.objects if ObjectService.object_is_basemesh(obj)]
        assert len(basemeshes) == 3, "three characters were generated into the collection"
    finally:
        _set_props(seed=0)


def test_batch_stamps_derived_seed_on_each_character():
    try:
        _minimal_scene()
        _set_props(batch_count=3, batch_strategy="GRID", batch_random_rotation=False)
        collection = _run_batch(777)
        expected = set(RandomizationService.derive_character_seeds(777, 3))
        stamped = set()
        for obj in collection.objects:
            if ObjectService.object_is_basemesh(obj):
                assert "mpfb_randomization_seed" in obj, "each basemesh carries the seed custom property"
                stamped.add(obj["mpfb_randomization_seed"])
        assert stamped == expected, "the stamped seeds are exactly the derived per-character seeds"
    finally:
        _set_props(seed=0)


def test_batch_grid_positions_follow_the_spec():
    try:
        _minimal_scene()
        _set_props(batch_count=3, batch_strategy="GRID", batch_random_rotation=False,
                   batch_spacing_x=2.0, batch_row_length=2, batch_row_shift_y=3.0)
        collection = _run_batch(31337)
        # No rig, so each basemesh is its own root and carries the placement directly.
        positions = set()
        for obj in collection.objects:
            if ObjectService.object_is_basemesh(obj):
                positions.add((round(obj.location[0], 4), round(obj.location[1], 4)))
        assert positions == {(0.0, 0.0), (2.0, 0.0), (0.0, 3.0)}, "grid positions follow spacing, row length and row shift"
    finally:
        _set_props(seed=0)


def test_batch_character_matches_single_operator_with_its_seed():
    # Requirement: a character's stamped seed reproduces that character in the single-character
    # operator. Build a batch, read one character's macro and seed, then run the single operator
    # with that seed and compare the macros.
    try:
        _minimal_scene()
        _set_props(batch_count=3, batch_strategy="GRID", batch_random_rotation=False)
        collection = _run_batch(9001)
        target = None
        for obj in collection.objects:
            if ObjectService.object_is_basemesh(obj):
                target = obj
                break
        assert target is not None
        batch_macro = _flatten_macro(TargetService.get_macro_info_dict_from_basemesh(target))
        seed = target["mpfb_randomization_seed"]

        # Clear the batch, then reproduce that one character with the single-character operator.
        _delete_all_humans()
        _delete_batch_collections()
        _set_props(seed=seed)
        ObjectService.deselect_and_deactivate_all()
        single = MockOperatorBase()
        MPFB_OT_Create_Random_Human_Operator.hardened_execute(single, bpy.context)
        single.mock_report.assert_no_errors()
        single_basemesh = _find_basemeshes()[0]
        single_macro = _flatten_macro(TargetService.get_macro_info_dict_from_basemesh(single_basemesh))

        assert batch_macro.keys() == single_macro.keys()
        for key in batch_macro:
            assert batch_macro[key] == approx(single_macro[key], abs=1e-4), \
                "Attribute " + key + " differs between the batch character and its stamped-seed reproduction"
    finally:
        _set_props(seed=0)
