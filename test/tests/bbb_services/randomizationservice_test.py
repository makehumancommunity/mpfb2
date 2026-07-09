import copy, random

from .. import RandomizationService, TargetService

_DISTRIBUTIONS = ["flat", "bell", "pyramid", "peak"]


def _spec():
    """A fresh default spec for a test to mutate."""
    return RandomizationService.get_default_phenotype_spec()


def test_randomizationservice_exists():
    assert RandomizationService is not None, "RandomizationService can be imported"


def test_default_spec_shape():
    spec = _spec()
    assert spec["version"] == 1, "The default spec has a version"
    phenotype = spec["phenotype"]
    assert phenotype["distribution"] == "bell", "The default distribution is bell"
    assert phenotype["discrete_race"] is False
    assert phenotype["discrete_gender"] is True
    assert phenotype["discrete_age"] is False
    for name in ["gender", "age", "muscle", "weight", "height", "proportions", "cupsize", "firmness"]:
        attribute = phenotype["attributes"][name]
        assert attribute["include"] is True, name + " is included by default"
        assert attribute["neutral"] == 0.5, name + " has neutral 0.5"
        assert attribute["deviation"] == 0.5, name + " has deviation 0.5"
    assert phenotype["attributes"]["race"]["include"] is True
    # The discrete attributes allow all of their values by default.
    assert phenotype["attributes"]["gender"]["allowed"] == ["female", "male"]
    assert phenotype["attributes"]["age"]["allowed"] == ["baby", "child", "young", "old"]
    assert phenotype["attributes"]["race"]["allowed"] == ["asian", "caucasian", "african"]


def test_get_discrete_value_names():
    assert RandomizationService.get_discrete_value_names("gender") == ["female", "male"]
    assert RandomizationService.get_discrete_value_names("age") == ["baby", "child", "young", "old"]
    assert RandomizationService.get_discrete_value_names("race") == ["asian", "caucasian", "african"]
    # The names must match the allowed lists the default spec is built from.
    phenotype = _spec()["phenotype"]["attributes"]
    for attribute in ["gender", "age", "race"]:
        assert RandomizationService.get_discrete_value_names(attribute) == phenotype[attribute]["allowed"]
    try:
        RandomizationService.get_discrete_value_names("muscle")
        assert False, "get_discrete_value_names should reject a non-discrete attribute"
    except ValueError:
        pass


def test_same_seed_produces_identical_dict():
    spec = _spec()
    first = RandomizationService.randomize_macro_info_dict(spec, random.Random(1234))
    second = RandomizationService.randomize_macro_info_dict(spec, random.Random(1234))
    assert first == second, "The same seed and spec produce an identical macro dict"


def test_different_seeds_produce_different_dicts():
    spec = _spec()
    first = RandomizationService.randomize_macro_info_dict(spec, random.Random(1))
    second = RandomizationService.randomize_macro_info_dict(spec, random.Random(2))
    assert first != second, "Different seeds produce different macro dicts"


def test_sample_value_respects_ranges():
    for distribution in _DISTRIBUTIONS:
        rng = random.Random(42)
        for _ in range(2000):
            neutral = 0.4
            deviation = 0.2
            value = RandomizationService.sample_value(distribution, neutral, deviation, rng)
            assert value >= 0.0 and value <= 1.0, distribution + " stays within the full range"
            assert value >= neutral - deviation - 1e-9, distribution + " stays within the deviation range (low)"
            assert value <= neutral + deviation + 1e-9, distribution + " stays within the deviation range (high)"


def test_sample_value_clamps_to_full_range():
    # A neutral near the edge with a large deviation must still stay within 0..1.
    for distribution in _DISTRIBUTIONS:
        rng = random.Random(7)
        for _ in range(1000):
            value = RandomizationService.sample_value(distribution, 0.95, 0.5, rng)
            assert value >= 0.0 and value <= 1.0, distribution + " is clamped to the full range"


def test_sample_value_zero_deviation():
    for distribution in _DISTRIBUTIONS:
        value = RandomizationService.sample_value(distribution, 0.3, 0.0, random.Random(0))
        assert value == 0.3, distribution + " with zero deviation returns the neutral value"


def test_continuous_race_sums_to_one():
    spec = _spec()
    for seed in range(20):
        macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))
        total = sum(macro["race"].values())
        assert abs(total - 1.0) < 1e-6, "Continuous race weights sum to ~1.0"


def test_discrete_race_picks_exactly_one():
    spec = _spec()
    spec["phenotype"]["discrete_race"] = True
    for seed in range(20):
        macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))
        values = list(macro["race"].values())
        assert values.count(1.0) == 1, "Discrete race sets exactly one weight to 1.0"
        assert values.count(0.0) == 2, "Discrete race sets the other two weights to 0.0"


def test_discrete_age_hits_an_anchor():
    spec = _spec()
    spec["phenotype"]["discrete_age"] = True
    anchors = {0.0, 0.1875, 0.5, 1.0}
    for seed in range(40):
        macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))
        assert macro["age"] in anchors, "Discrete age is exactly one of the four anchors"


def test_discrete_gender_respects_allowed_subset():
    spec = _spec()
    spec["phenotype"]["attributes"]["gender"]["allowed"] = ["female"]
    for seed in range(40):
        macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))
        assert macro["gender"] == 0.0, "Only female allowed produces female (0.0)"


def test_discrete_age_respects_allowed_subset():
    spec = _spec()
    spec["phenotype"]["discrete_age"] = True
    spec["phenotype"]["attributes"]["age"]["allowed"] = ["young", "old"]
    for seed in range(40):
        macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))
        assert macro["age"] in {0.5, 1.0}, "Only young/old allowed restricts the discrete age"


def test_discrete_race_respects_allowed_subset():
    spec = _spec()
    spec["phenotype"]["discrete_race"] = True
    spec["phenotype"]["attributes"]["race"]["allowed"] = ["asian"]
    for seed in range(20):
        macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))
        assert macro["race"]["asian"] == 1.0, "Only asian allowed always picks asian"
        assert macro["race"]["caucasian"] == 0.0
        assert macro["race"]["african"] == 0.0


def test_empty_allowed_gender_falls_back_to_neutral():
    spec = _spec()
    spec["phenotype"]["attributes"]["gender"]["allowed"] = []
    spec["phenotype"]["attributes"]["gender"]["neutral"] = 0.5
    macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(3))
    assert macro["gender"] == 0.5, "No allowed gender is treated as excluded (neutral)"


def test_empty_allowed_age_falls_back_to_neutral():
    spec = _spec()
    spec["phenotype"]["discrete_age"] = True
    spec["phenotype"]["attributes"]["age"]["allowed"] = []
    spec["phenotype"]["attributes"]["age"]["neutral"] = 0.5
    macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(3))
    assert macro["age"] == 0.5, "No allowed age is treated as excluded (neutral)"


def test_empty_allowed_discrete_race_falls_back_to_even_mix():
    spec = _spec()
    spec["phenotype"]["discrete_race"] = True
    spec["phenotype"]["attributes"]["race"]["allowed"] = []
    macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(3))
    for name in ["asian", "caucasian", "african"]:
        assert abs(macro["race"][name] - 1.0 / 3.0) < 1e-6, "No allowed race is treated as excluded (even mix)"


def test_excluded_attribute_uses_neutral():
    spec = _spec()
    spec["phenotype"]["attributes"]["weight"]["include"] = False
    for seed in range(10):
        macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))
        assert macro["weight"] == 0.5, "An excluded attribute comes out at its neutral value"


def test_neutral_override_is_respected():
    spec = _spec()
    # Exclude muscle and override its neutral, so the exact value is deterministic.
    spec["phenotype"]["attributes"]["muscle"]["include"] = False
    spec["phenotype"]["attributes"]["muscle"]["neutral"] = 0.2
    macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(0))
    assert macro["muscle"] == 0.2, "A neutral override is respected for an excluded attribute"


def test_breast_constraint_male_side_uses_neutral():
    spec = _spec()
    # Force a male character by excluding gender with a male-side neutral.
    spec["phenotype"]["attributes"]["gender"]["include"] = False
    spec["phenotype"]["attributes"]["gender"]["neutral"] = 1.0
    # Force a young-adult age so only the gender guard can apply.
    spec["phenotype"]["attributes"]["age"]["include"] = False
    spec["phenotype"]["attributes"]["age"]["neutral"] = 0.7
    for seed in range(10):
        macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))
        assert macro["cupsize"] == 0.5, "Male-side gender forces neutral cupsize"
        assert macro["firmness"] == 0.5, "Male-side gender forces neutral firmness"


def test_breast_constraint_young_age_uses_neutral():
    spec = _spec()
    # Female character, but below the young-adult threshold.
    spec["phenotype"]["attributes"]["gender"]["include"] = False
    spec["phenotype"]["attributes"]["gender"]["neutral"] = 0.0
    spec["phenotype"]["attributes"]["age"]["include"] = False
    spec["phenotype"]["attributes"]["age"]["neutral"] = 0.2
    for seed in range(10):
        macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))
        assert macro["cupsize"] == 0.5, "Age below the threshold forces neutral cupsize"
        assert macro["firmness"] == 0.5, "Age below the threshold forces neutral firmness"


def test_breast_constraint_allows_adult_female():
    spec = _spec()
    # Female adult with a wide deviation, so cupsize should vary away from neutral.
    spec["phenotype"]["attributes"]["gender"]["include"] = False
    spec["phenotype"]["attributes"]["gender"]["neutral"] = 0.0
    spec["phenotype"]["attributes"]["age"]["include"] = False
    spec["phenotype"]["attributes"]["age"]["neutral"] = 0.8
    spec["phenotype"]["attributes"]["cupsize"]["deviation"] = 0.4
    values = set()
    for seed in range(20):
        macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))
        values.add(macro["cupsize"])
    assert len(values) > 1, "An adult female gets a randomized (non-constant) cupsize"


def test_result_matches_default_macro_dict_shape():
    spec = _spec()
    macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(0))
    assert set(macro.keys()) == set(TargetService.get_default_macro_info_dict().keys()), \
        "The result has the same shape as the default macro info dict"
    assert set(macro["race"].keys()) == {"asian", "caucasian", "african"}


def test_preset_round_trip_is_lossless():
    spec = _spec()
    text = RandomizationService.serialize_spec_to_json_string(spec)
    restored = RandomizationService.deserialize_spec_from_json_string(text)
    assert restored == spec, "A spec survives a JSON round-trip unchanged"


def test_preset_round_trip_preserves_unknown_sections():
    spec = _spec()
    # A later sub-feature would add sibling sections; these must survive a round-trip.
    spec["creation"] = {"scale_factor": "DECIMETER", "mask_helpers": True}
    spec["details"] = {"placeholder": 1}
    original = copy.deepcopy(spec)
    text = RandomizationService.serialize_spec_to_json_string(spec)
    restored = RandomizationService.deserialize_spec_from_json_string(text)
    assert restored == original, "Unknown sections are preserved across a round-trip"


def _macro(age, gender, race):
    """A minimal macro info dict for exercising describe_macro_info_dict."""
    return {"age": age, "gender": gender, "race": race}


def test_describe_age_label_is_closest_anchor():
    for value, expected in [(0.0, "baby"), (0.1875, "child"), (0.5, "young"), (1.0, "old")]:
        macro = _macro(value, 0.0, {"african": 0.0, "asian": 0.0, "caucasian": 1.0})
        assert (" " + expected + " ") in RandomizationService.describe_macro_info_dict(macro, 1), \
            "Age anchor " + str(value) + " is labelled " + expected
    # Between baby (0.0) and child (0.1875), 0.1 is closer to child.
    macro = _macro(0.1, 0.0, {"african": 0.0, "asian": 0.0, "caucasian": 1.0})
    assert " child (" in RandomizationService.describe_macro_info_dict(macro, 1), \
        "0.1 labels as child (closest anchor), not baby"


def test_describe_gender_bands():
    race = {"african": 0.0, "asian": 0.0, "caucasian": 1.0}
    assert " female (" in RandomizationService.describe_macro_info_dict(_macro(0.5, 0.2, race), 1)
    assert " neutral (" in RandomizationService.describe_macro_info_dict(_macro(0.5, 0.5, race), 1)
    assert " male (" in RandomizationService.describe_macro_info_dict(_macro(0.5, 0.9, race), 1)


def test_describe_race_label():
    caucasian = {"african": 0.0, "asian": 0.0, "caucasian": 1.0}
    assert " caucasian (" in RandomizationService.describe_macro_info_dict(_macro(0.5, 0.0, caucasian), 1)
    mixed = {"african": 0.34, "asian": 0.33, "caucasian": 0.33}
    assert " mixed race (" in RandomizationService.describe_macro_info_dict(_macro(0.5, 0.0, mixed), 1)


def test_describe_article_matches_age_label():
    race = {"african": 0.0, "asian": 0.0, "caucasian": 1.0}
    assert RandomizationService.describe_macro_info_dict(_macro(1.0, 0.0, race), 1).startswith("Generated with seed 1: An old ")
    assert RandomizationService.describe_macro_info_dict(_macro(0.5, 0.0, race), 1).startswith("Generated with seed 1: A young ")


def test_describe_full_strings():
    caucasian = {"african": 0.0, "asian": 0.0, "caucasian": 1.0}
    assert RandomizationService.describe_macro_info_dict(_macro(0.6, 0.1, caucasian), 123) == \
        "Generated with seed 123: A young (0.6) caucasian (0.0/0.0/1.0) female (0.1)"
    mixed_even = {"african": 0.3, "asian": 0.3, "caucasian": 0.3}
    assert RandomizationService.describe_macro_info_dict(_macro(0.9, 0.9, mixed_even), 345) == \
        "Generated with seed 345: An old (0.9) mixed race (0.3/0.3/0.3) male (0.9)"
    mixed = {"african": 0.4, "asian": 0.4, "caucasian": 0.2}
    assert RandomizationService.describe_macro_info_dict(_macro(0.0, 0.55, mixed), 678) == \
        "Generated with seed 678: A baby (0.0) mixed race (0.4/0.4/0.2) neutral (0.55)"
