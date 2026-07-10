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
    assert spec["version"] == 5, "The default spec has a version"
    phenotype = spec["phenotype"]
    assert phenotype["distribution"] == "bell", "The default distribution is bell"
    assert phenotype["discrete_race"] is False
    assert phenotype["discrete_gender"] is True
    assert phenotype["discrete_age"] is True
    assert phenotype["breast_gender_cutoff"] == 0.6, "The default breast gender cutoff is 0.6"
    assert phenotype["breast_age_cutoff"] == 0.4, "The default breast age cutoff is 0.4"
    for name in ["gender", "age", "muscle", "weight", "height", "proportions", "cupsize", "firmness"]:
        attribute = phenotype["attributes"][name]
        assert attribute["include"] is True, name + " is included by default"
        assert attribute["neutral"] == 0.5, name + " has neutral 0.5"
        assert attribute["deviation"] == 0.5, name + " has deviation 0.5"
    assert phenotype["attributes"]["race"]["include"] is True
    # The discrete attributes allow all of their values by default.
    assert phenotype["attributes"]["gender"]["allowed"] == ["female", "male"]
    assert phenotype["attributes"]["age"]["allowed"] == ["baby", "child", "young", "middleage", "old"]
    assert phenotype["attributes"]["race"]["allowed"] == ["asian", "caucasian", "african"]


def test_get_discrete_value_names():
    assert RandomizationService.get_discrete_value_names("gender") == ["female", "male"]
    assert RandomizationService.get_discrete_value_names("age") == ["baby", "child", "young", "middleage", "old"]
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
    anchors = {0.0, 0.1875, 0.5, 0.75, 1.0}
    for seed in range(40):
        macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))
        assert macro["age"] in anchors, "Discrete age is exactly one of the five anchors"


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


def test_breast_gender_cutoff_is_configurable():
    # A mid-range (androgynous) gender of 0.3 is below the default 0.4 cutoff, so it gets breasts,
    # but not below a lowered 0.2 cutoff, where it is forced neutral.
    spec = _spec()
    spec["phenotype"]["attributes"]["gender"]["include"] = False
    spec["phenotype"]["attributes"]["gender"]["neutral"] = 0.3
    spec["phenotype"]["attributes"]["age"]["include"] = False
    spec["phenotype"]["attributes"]["age"]["neutral"] = 0.8
    spec["phenotype"]["attributes"]["cupsize"]["deviation"] = 0.4

    spec["phenotype"]["breast_gender_cutoff"] = 0.4
    default_cutoff = {RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))["cupsize"] for seed in range(20)}
    assert len(default_cutoff) > 1, "Gender 0.3 is female enough at the default 0.4 cutoff and gets a randomized cupsize"

    spec["phenotype"]["breast_gender_cutoff"] = 0.2
    for seed in range(20):
        macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))
        assert macro["cupsize"] == 0.5, "Gender 0.3 is above a lowered 0.2 cutoff and gets neutral cupsize"


def test_breast_age_cutoff_is_configurable():
    # A young-ish age of 0.45 is at/above the default 0.4 cutoff, so it gets breasts, but below a
    # raised 0.5 cutoff, where it is forced neutral.
    spec = _spec()
    spec["phenotype"]["attributes"]["gender"]["include"] = False
    spec["phenotype"]["attributes"]["gender"]["neutral"] = 0.0
    spec["phenotype"]["attributes"]["age"]["include"] = False
    spec["phenotype"]["attributes"]["age"]["neutral"] = 0.45
    spec["phenotype"]["attributes"]["cupsize"]["deviation"] = 0.4

    spec["phenotype"]["breast_age_cutoff"] = 0.4
    default_cutoff = {RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))["cupsize"] for seed in range(20)}
    assert len(default_cutoff) > 1, "Age 0.45 is above the default 0.4 cutoff and gets a randomized cupsize"

    spec["phenotype"]["breast_age_cutoff"] = 0.5
    for seed in range(20):
        macro = RandomizationService.randomize_macro_info_dict(spec, random.Random(seed))
        assert macro["cupsize"] == 0.5, "Age 0.45 is below a raised 0.5 cutoff and gets neutral cupsize"


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
    for value, expected in [(0.0, "baby"), (0.1875, "child"), (0.5, "young"), (0.75, "middleage"), (1.0, "old")]:
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


# --- Skin randomization -----------------------------------------------------------------

_NO_RACE = {"asian": 0.0, "caucasian": 0.0, "african": 0.0}


def _skin_spec(**overrides):
    """A default spec with all skin filters off, so a test only turns on what it needs."""
    spec = RandomizationService.get_default_phenotype_spec()
    spec["assets"]["skin"].update({
        "enabled": True, "match_gender": False, "match_age": False, "match_race": False,
        "fallback": True, "pack": "", "include": "", "exclude": ""
        })
    spec["assets"]["skin"].update(overrides)
    return spec


def _cands(*names):
    """Build candidate dicts (no pack) from a list of skin names."""
    return [{"name": name, "path": "/skins/" + name + ".mhmat", "pack": None} for name in names]


def _picks(spec, macro, candidates, seeds=range(25)):
    """The set of names picked across several seeds (to exercise the whole pool)."""
    return {RandomizationService.pick_random_skin(spec, macro, candidates, random.Random(seed))["name"]
            for seed in seeds}


def test_default_spec_has_skin_assets():
    skin = _spec()["assets"]["skin"]
    assert skin["enabled"] is True
    assert skin["match_gender"] is True and skin["match_age"] is True and skin["match_race"] is True
    assert skin["fallback"] is True
    assert skin["pack"] == ""
    assert skin["include"] == ""
    assert skin["exclude"] == "special_suit"
    assert skin["skin_type"] == "MAKESKIN"
    assert skin["material_instances"] is True


def test_skin_gender_label_splits_at_half():
    assert RandomizationService.skin_gender_label({"gender": 0.0}) == "female"
    assert RandomizationService.skin_gender_label({"gender": 0.49}) == "female"
    assert RandomizationService.skin_gender_label({"gender": 0.5}) == "male"
    assert RandomizationService.skin_gender_label({"gender": 1.0}) == "male"


def test_skin_age_label_five_bands():
    assert RandomizationService.skin_age_label({"age": 0.0}) == "baby"
    assert RandomizationService.skin_age_label({"age": 0.2}) == "child"
    assert RandomizationService.skin_age_label({"age": 0.5}) == "young"
    assert RandomizationService.skin_age_label({"age": 0.75}) == "middleage"
    assert RandomizationService.skin_age_label({"age": 0.9}) == "old"
    # Band boundaries: middleage occupies [0.65, 0.85).
    assert RandomizationService.skin_age_label({"age": 0.64}) == "young"
    assert RandomizationService.skin_age_label({"age": 0.65}) == "middleage"
    assert RandomizationService.skin_age_label({"age": 0.84}) == "middleage"
    assert RandomizationService.skin_age_label({"age": 0.85}) == "old"


def test_skin_race_label_dominant_or_none():
    assert RandomizationService.skin_race_label({"race": {"asian": 0.6, "caucasian": 0.2, "african": 0.2}}) == "asian"
    assert RandomizationService.skin_race_label({"race": {"asian": 0.2, "caucasian": 0.6, "african": 0.2}}) == "caucasian"
    assert RandomizationService.skin_race_label({"race": {"asian": 0.2, "caucasian": 0.2, "african": 0.6}}) == "african"
    assert RandomizationService.skin_race_label({"race": {"asian": 0.34, "caucasian": 0.33, "african": 0.33}}) is None


def test_skin_gender_filter_male_not_matching_female():
    macro = _macro(0.5, 1.0, _NO_RACE)
    spec = _skin_spec(match_gender=True, fallback=False)
    cands = _cands("young_caucasian_female2", "young_caucasian_male")
    assert _picks(spec, macro, cands) == {"young_caucasian_male"}, "male filter must not match a female name"


def test_skin_gender_filter_female_matches_female_name():
    macro = _macro(0.5, 0.0, _NO_RACE)
    spec = _skin_spec(match_gender=True, fallback=False)
    cands = _cands("young_caucasian_female2", "young_caucasian_male")
    assert _picks(spec, macro, cands) == {"young_caucasian_female2"}


def test_skin_race_filter_asian_not_matching_caucasian():
    macro = _macro(0.5, 0.0, {"asian": 1.0, "caucasian": 0.0, "african": 0.0})
    spec = _skin_spec(match_race=True, fallback=False)
    cands = _cands("young_caucasian_male", "young_asian_male")
    assert _picks(spec, macro, cands) == {"young_asian_male"}, "asian filter must not match a caucasian name"


def test_skin_race_filter_caucasian_and_african_match():
    caucasian = _skin_spec(match_race=True, fallback=False)
    cands = _cands("young_caucasian_male", "young_asian_male", "young_african_male")
    assert _picks(caucasian, _macro(0.5, 0.0, {"asian": 0.0, "caucasian": 1.0, "african": 0.0}), cands) == {"young_caucasian_male"}
    assert _picks(caucasian, _macro(0.5, 0.0, {"asian": 0.0, "caucasian": 0.0, "african": 1.0}), cands) == {"young_african_male"}


def test_skin_matching_is_case_insensitive():
    macro = _macro(0.5, 0.0, _NO_RACE)
    spec = _skin_spec(match_gender=True, fallback=False)
    cands = _cands("Young_Caucasian_FEMALE")
    assert _picks(spec, macro, cands) == {"Young_Caucasian_FEMALE"}


def test_skin_age_filter_middleage():
    macro = _macro(0.75, 0.0, _NO_RACE)
    spec = _skin_spec(match_age=True, fallback=False)
    cands = _cands("young_female", "middleage_female", "old_female")
    assert _picks(spec, macro, cands) == {"middleage_female"}


def test_skin_combined_phenotype_filters():
    macro = _macro(0.5, 0.0, {"asian": 0.0, "caucasian": 1.0, "african": 0.0})
    spec = _skin_spec(match_gender=True, match_age=True, match_race=True, fallback=False)
    cands = _cands("young_caucasian_female", "young_caucasian_male", "old_caucasian_female", "young_asian_female")
    assert _picks(spec, macro, cands) == {"young_caucasian_female"}


def test_skin_pack_filter():
    macro = _macro(0.5, 0.0, _NO_RACE)
    spec = _skin_spec(pack="system", fallback=False)
    cands = [
        {"name": "a", "path": "/a.mhmat", "pack": "makehuman_system_assets"},
        {"name": "b", "path": "/b.mhmat", "pack": "third_party_pack"},
        {"name": "c", "path": "/c.mhmat", "pack": None}
        ]
    assert _picks(spec, macro, cands) == {"a"}, "only skins from a matching pack (not None) are kept"


def test_skin_include_keeps_any_of():
    macro = _macro(0.5, 0.0, _NO_RACE)
    spec = _skin_spec(include="brown, pale")
    cands = _cands("skin_brown", "skin_pale", "skin_dark")
    assert _picks(spec, macro, cands) == {"skin_brown", "skin_pale"}


def test_skin_exclude_removes_any_of():
    macro = _macro(0.5, 0.0, _NO_RACE)
    spec = _skin_spec(exclude="special_suit, wip")
    cands = _cands("normal", "young_male_special_suit", "test_wip")
    assert _picks(spec, macro, cands) == {"normal"}


def test_skin_keyword_whitespace_and_empty_entries_ignored():
    macro = _macro(0.5, 0.0, _NO_RACE)
    spec = _skin_spec(include=" brown , , ")
    cands = _cands("skin_brown", "skin_pale")
    assert _picks(spec, macro, cands) == {"skin_brown"}, "a single effective keyword behaves as a plain substring"


def test_skin_single_keyword_without_commas_is_plain_substring():
    macro = _macro(0.5, 0.0, _NO_RACE)
    spec = _skin_spec(include="brown")
    cands = _cands("skin_brown", "skin_pale")
    assert _picks(spec, macro, cands) == {"skin_brown"}


def test_skin_fallback_relaxes_age_first():
    # Candidate matches gender and race but has the wrong age. With fallback, age is dropped.
    macro = _macro(0.75, 0.0, {"asian": 0.0, "caucasian": 1.0, "african": 0.0})
    spec = _skin_spec(match_gender=True, match_age=True, match_race=True, fallback=True)
    cands = _cands("young_caucasian_female")
    assert _picks(spec, macro, cands) == {"young_caucasian_female"}


def test_skin_fallback_stops_at_first_non_empty_pool():
    # Dropping age alone already matches, so race/gender must not be relaxed further: the
    # asian candidate (wrong race) stays excluded.
    macro = _macro(0.75, 0.0, {"asian": 0.0, "caucasian": 1.0, "african": 0.0})
    spec = _skin_spec(match_gender=True, match_age=True, match_race=True, fallback=True)
    cands = _cands("young_caucasian_female", "young_asian_female")
    assert _picks(spec, macro, cands) == {"young_caucasian_female"}


def test_skin_fallback_does_not_relax_exclude():
    macro = _macro(0.5, 0.0, _NO_RACE)
    spec = _skin_spec(exclude="suit", fallback=True)
    cands = _cands("young_male_suit")
    assert RandomizationService.pick_random_skin(spec, macro, cands, random.Random(0)) is None


def test_skin_empty_pool_returns_none():
    macro = _macro(0.5, 0.0, _NO_RACE)
    assert RandomizationService.pick_random_skin(_skin_spec(), macro, [], random.Random(0)) is None


def test_skin_disabled_returns_none_and_draws_nothing():
    macro = _macro(0.5, 0.0, _NO_RACE)
    spec = _skin_spec(enabled=False)
    cands = _cands("a", "b", "c")
    rng = random.Random(0)
    assert RandomizationService.pick_random_skin(spec, macro, cands, rng) is None
    # No draw was consumed, so the generator still yields its very first value.
    assert rng.random() == random.Random(0).random()


def test_v1_spec_without_assets_disables_skin():
    macro = _macro(0.5, 0.0, _NO_RACE)
    spec = _spec()
    del spec["assets"]
    cands = _cands("a", "b")
    assert RandomizationService.pick_random_skin(spec, macro, cands, random.Random(0)) is None


def test_skin_same_seed_same_pick():
    macro = _macro(0.5, 0.0, _NO_RACE)
    spec = _skin_spec()
    cands = _cands("a", "b", "c", "d", "e")
    first = RandomizationService.pick_random_skin(spec, macro, cands, random.Random(42))
    second = RandomizationService.pick_random_skin(spec, macro, cands, random.Random(42))
    assert first == second


def test_skin_shuffling_candidates_does_not_change_pick():
    macro = _macro(0.5, 0.0, _NO_RACE)
    spec = _skin_spec()
    cands = _cands("a", "b", "c", "d", "e")
    original = RandomizationService.pick_random_skin(spec, macro, list(cands), random.Random(7))
    shuffled = list(cands)
    random.Random(99).shuffle(shuffled)
    reshuffled = RandomizationService.pick_random_skin(spec, macro, shuffled, random.Random(7))
    assert original["name"] == reshuffled["name"], "the pick is independent of candidate order"


# --- Bodypart randomization -------------------------------------------------------------


def _hair_spec(**overrides):
    """A default hair section with all filters off, so a test only turns on what it needs."""
    section = {
        "enabled": True, "match_gender": False, "fallback": True,
        "pack": "", "include": "", "exclude": "", "randomize_alt_materials": False
        }
    section.update(overrides)
    return section


def _bp_picks(section, macro, candidates, seeds=range(25)):
    """The set of names pick_random_bodypart returns across several seeds."""
    return {RandomizationService.pick_random_bodypart(section, macro, candidates, random.Random(seed))["name"]
            for seed in seeds}


def test_default_spec_has_bodypart_sections():
    assets = _spec()["assets"]
    assert assets["asset_material_type"] == "MAKESKIN", "the shared asset material defaults to MakeSkin"
    assert assets["eyes"]["mode"] == "LOWPOLY", "eyes default to low-poly"
    assert assets["eyes"]["randomize_alt_materials"] is True, "eyes randomize iris colour by default"
    assert assets["hair"]["enabled"] is True
    assert assets["hair"]["match_gender"] is False, "hair gender filter is off by default"
    assert assets["hair"]["randomize_alt_materials"] is False
    for name in ["eyebrows", "eyelashes", "teeth", "tongue"]:
        assert assets[name]["enabled"] is True, name + " is enabled by default"


def test_bodypart_type_lists_and_defaults():
    assert RandomizationService.get_bodypart_types() == ["eyebrows", "eyelashes", "eyes", "hair", "teeth", "tongue"]
    assert RandomizationService.get_plain_bodypart_types() == ["eyebrows", "eyelashes", "teeth", "tongue"]
    assert RandomizationService.get_default_bodypart_asset_spec("eyes")["mode"] == "LOWPOLY"
    assert RandomizationService.get_default_bodypart_asset_spec("hair")["match_gender"] is False
    assert "enabled" in RandomizationService.get_default_bodypart_asset_spec("teeth")


def test_bodypart_disabled_returns_none_and_draws_nothing():
    macro = _macro(0.5, 0.0, _NO_RACE)
    rng = random.Random(0)
    assert RandomizationService.pick_random_bodypart(_hair_spec(enabled=False), macro, _cands("a", "b"), rng) is None
    # No draw was consumed, so the generator still yields its very first value.
    assert rng.random() == random.Random(0).random()


def test_bodypart_missing_section_is_disabled():
    # A version-2 preset has no bodypart subsection; an empty section is treated as disabled.
    macro = _macro(0.5, 0.0, _NO_RACE)
    assert RandomizationService.pick_random_bodypart({}, macro, _cands("a"), random.Random(0)) is None


def test_bodypart_empty_pool_returns_none():
    macro = _macro(0.5, 0.0, _NO_RACE)
    assert RandomizationService.pick_random_bodypart(_hair_spec(), macro, [], random.Random(0)) is None


def test_bodypart_include_exclude_pack_filters():
    macro = _macro(0.5, 0.0, _NO_RACE)
    assert _bp_picks(_hair_spec(include="long"), macro, _cands("long_hair", "short_hair")) == {"long_hair"}
    assert _bp_picks(_hair_spec(exclude="short"), macro, _cands("long_hair", "short_hair")) == {"long_hair"}
    cands = [
        {"name": "a", "path": "/hair/a.mhclo", "pack": "PackOne"},
        {"name": "b", "path": "/hair/b.mhclo", "pack": "Other"}
        ]
    assert _bp_picks(_hair_spec(pack="one"), macro, cands) == {"a"}


def test_bodypart_hair_gender_filter_male_not_matching_female():
    macro = _macro(0.5, 1.0, _NO_RACE)  # male side
    section = _hair_spec(match_gender=True)
    # "male" must not match inside "female_bun"; only the male-named style is eligible.
    assert _bp_picks(section, macro, _cands("male_cut", "female_bun")) == {"male_cut"}


def test_bodypart_hair_relax_drops_only_gender():
    macro = _macro(0.5, 1.0, _NO_RACE)  # male side, but no male-named hair
    # With fallback the gender filter is dropped and both unlabeled styles become eligible.
    assert _bp_picks(_hair_spec(match_gender=True, fallback=True), macro, _cands("bun", "braid")) == {"bun", "braid"}
    # But the exclude filter is never relaxed.
    section = _hair_spec(match_gender=True, fallback=True, exclude="braid")
    assert _bp_picks(section, macro, _cands("bun", "braid")) == {"bun"}


def test_bodypart_hair_no_match_no_fallback_returns_none():
    macro = _macro(0.5, 1.0, _NO_RACE)  # male side, no male-named hair
    section = _hair_spec(match_gender=True, fallback=False)
    assert RandomizationService.pick_random_bodypart(section, macro, _cands("bun", "braid"), random.Random(0)) is None


def test_alt_material_uniform_over_default_and_alternatives():
    picks = {RandomizationService.pick_random_alternative_material("d", ["a", "b"], random.Random(seed))
             for seed in range(30)}
    assert picks == {"d", "a", "b"}, "the pick is uniform over the default plus its alternatives"


def test_alt_material_order_independent():
    first = RandomizationService.pick_random_alternative_material("d", ["b", "a", "c"], random.Random(3))
    second = RandomizationService.pick_random_alternative_material("d", ["c", "a", "b"], random.Random(3))
    assert first == second, "the pick does not depend on the alternatives' order"


def test_alt_material_dedups_default_and_duplicates():
    picks = {RandomizationService.pick_random_alternative_material("d", ["d", "a", "a"], random.Random(seed))
             for seed in range(25)}
    assert picks == {"d", "a"}, "duplicates and the default are collapsed"


def test_alt_material_no_alternatives_returns_default_without_drawing():
    rng = random.Random(0)
    assert RandomizationService.pick_random_alternative_material("d", [], rng) == "d"
    # A single (or empty) pool consumes no draw, so a disabled toggle does not shift the seed.
    assert rng.random() == random.Random(0).random()


def test_v2_spec_deserializes_with_bodyparts_disabled():
    # Simulate a version-2 preset: only the skin asset section exists.
    spec = _spec()
    spec["version"] = 2
    spec["assets"] = {"skin": RandomizationService.get_default_skin_asset_spec()}
    text = RandomizationService.serialize_spec_to_json_string(spec)
    restored = RandomizationService.deserialize_spec_from_json_string(text)
    macro = _macro(0.5, 0.0, _NO_RACE)
    assert RandomizationService.pick_random_bodypart(restored["assets"].get("hair", {}), macro, _cands("a"), random.Random(0)) is None


# --- Clothes randomization --------------------------------------------------------------


def _slot(enabled=True, chance=100, pack="", include_any="", include_female="", include_male="", exclude=""):
    """One clothes slot section, all filters empty by default (a test sets what it needs)."""
    return {
        "enabled": enabled, "chance": chance, "pack": pack,
        "include_any": include_any, "include_female": include_female,
        "include_male": include_male, "exclude": exclude
        }


def _clothes(**slots):
    """A clothes section holding only the given slots; every other slot is absent (disabled)."""
    return dict(slots)


def _cc(*names):
    """Build clothes candidate dicts (no pack) from a list of asset names."""
    return [{"name": name, "path": "/clothes/" + name + ".mhclo", "pack": None} for name in names]


def _picked(results, slot):
    """The name picked for a slot in a pick_random_clothes result list, or None."""
    for result in results:
        if result["slot"] == slot:
            return result["pick"]["name"] if result["pick"] else None
    return None


def _warning(results, slot):
    """The warning code recorded for a slot in a pick_random_clothes result list, or None."""
    for result in results:
        if result["slot"] == slot:
            return result["warning"]
    return None


def _clothes_picks(section, macro, candidates, slot, seeds=range(40)):
    """The set of names picked for a slot across several seeds (to exercise the whole pool)."""
    names = set()
    for seed in seeds:
        results = RandomizationService.pick_random_clothes(section, macro, candidates, random.Random(seed))
        name = _picked(results, slot)
        if name is not None:
            names.add(name)
    return names


def test_default_spec_has_clothes_section():
    clothes = _spec()["assets"]["clothes"]
    assert set(clothes.keys()) == set(RandomizationService.get_clothes_slots())
    # Default enablement is "casual everyday": full body, upper body, lower body and feet on.
    for slot in ["full_body", "upper_body", "lower_body", "feet"]:
        assert clothes[slot]["enabled"] is True, slot + " is enabled by default"
    for slot in ["head", "hands", "underwear", "accessories"]:
        assert clothes[slot]["enabled"] is False, slot + " is disabled by default"
    assert clothes["full_body"]["chance"] == 25
    assert clothes["upper_body"]["chance"] == 100
    assert "dress,gown" in clothes["full_body"]["include_female"]


def test_clothes_slot_lists_and_defaults():
    assert RandomizationService.get_clothes_slots() == [
        "head", "full_body", "upper_body", "lower_body", "hands", "feet", "underwear", "accessories"]
    default_head = RandomizationService.get_default_clothes_asset_spec("head")
    assert default_head["chance"] == 20
    assert default_head["enabled"] is False
    assert "hat" in default_head["include_any"]


def test_clothes_all_disabled_draws_nothing():
    macro = _macro(0.5, 0.0, _NO_RACE)
    rng = random.Random(0)
    results = RandomizationService.pick_random_clothes({}, macro, _cc("hat1"), rng)
    assert results == [], "no enabled slot produces no results"
    # No draw was consumed, so the generator still yields its very first value.
    assert rng.random() == random.Random(0).random()


def test_clothes_two_draws_per_enabled_slot_regardless_of_outcome():
    macro = _macro(0.5, 0.0, _NO_RACE)
    # A single enabled slot that never fires (chance 0) still consumes exactly two draws.
    rng = random.Random(0)
    RandomizationService.pick_random_clothes(
        _clothes(head=_slot(chance=0, include_any="hat")), macro, _cc("hat1"), rng)
    reference = random.Random(0)
    reference.random()
    reference.random()
    assert rng.random() == reference.random(), "an enabled slot consumes exactly two draws"


def test_clothes_gendered_include_is_a_union():
    female = _macro(0.5, 0.0, _NO_RACE)
    male = _macro(0.5, 1.0, _NO_RACE)
    section = _clothes(upper_body=_slot(include_any="shirt", include_female="blouse", include_male="tanktop"))
    cands = _cc("shirt1", "blouse1", "tanktop1")
    # A female character draws from the common list unioned with the female list.
    assert _clothes_picks(section, female, cands, "upper_body") == {"shirt1", "blouse1"}
    # A male character draws from the common list unioned with the male list.
    assert _clothes_picks(section, male, cands, "upper_body") == {"shirt1", "tanktop1"}


def test_clothes_exclude_and_pack_filters():
    macro = _macro(0.5, 0.0, _NO_RACE)
    section = _clothes(head=_slot(include_any="hat", exclude="straw"))
    assert _clothes_picks(section, macro, _cc("felt_hat", "straw_hat"), "head") == {"felt_hat"}
    packed = [
        {"name": "hat_a", "path": "/clothes/hat_a.mhclo", "pack": "PackOne"},
        {"name": "hat_b", "path": "/clothes/hat_b.mhclo", "pack": "Other"}
        ]
    assert _clothes_picks(_clothes(head=_slot(include_any="hat", pack="one")), macro, packed, "head") == {"hat_a"}


def test_clothes_empty_include_no_pack_is_empty_pool():
    macro = _macro(0.5, 0.0, _NO_RACE)
    # An unmapped slot (no include keywords, no pack) never picks arbitrary garments, even
    # though candidates exist; the slot fires but its pool is empty.
    results = RandomizationService.pick_random_clothes(
        _clothes(head=_slot(chance=100)), macro, _cc("hat1", "coat1"), random.Random(0))
    assert _picked(results, "head") is None
    assert _warning(results, "head") == "empty_pool"


def test_clothes_empty_include_with_pack_uses_pack():
    macro = _macro(0.5, 0.0, _NO_RACE)
    packed = [
        {"name": "a", "path": "/clothes/a.mhclo", "pack": "PackOne"},
        {"name": "b", "path": "/clothes/b.mhclo", "pack": "Other"}
        ]
    # With no include keywords but a pack term, the pool is the pack's clothes.
    assert _clothes_picks(_clothes(head=_slot(pack="one")), macro, packed, "head") == {"a"}


def test_clothes_chance_zero_never_fires_hundred_always_fires():
    macro = _macro(0.5, 0.0, _NO_RACE)
    never = _clothes(head=_slot(chance=0, include_any="hat"))
    assert _clothes_picks(never, macro, _cc("hat1", "hat2"), "head") == set()
    always = _clothes(head=_slot(chance=100, include_any="hat"))
    assert _clothes_picks(always, macro, _cc("hat1", "hat2"), "head") == {"hat1", "hat2"}


def test_clothes_full_body_suppresses_separates():
    macro = _macro(0.5, 0.0, _NO_RACE)
    section = _clothes(
        full_body=_slot(chance=100, include_any="suit"),
        upper_body=_slot(chance=100, include_any="shirt"),
        lower_body=_slot(chance=100, include_any="pants"))
    results = RandomizationService.pick_random_clothes(section, macro, _cc("suit1", "shirt1", "pants1"), random.Random(0))
    assert _picked(results, "full_body") == "suit1"
    assert _picked(results, "upper_body") is None, "upper body is suppressed by the full body garment"
    assert _picked(results, "lower_body") is None, "lower body is suppressed by the full body garment"


def test_clothes_full_body_miss_runs_separates():
    macro = _macro(0.5, 0.0, _NO_RACE)
    section = _clothes(
        full_body=_slot(chance=0, include_any="suit"),
        upper_body=_slot(chance=100, include_any="shirt"),
        lower_body=_slot(chance=100, include_any="pants"))
    results = RandomizationService.pick_random_clothes(section, macro, _cc("suit1", "shirt1", "pants1"), random.Random(0))
    assert _picked(results, "full_body") is None
    assert _picked(results, "upper_body") == "shirt1"
    assert _picked(results, "lower_body") == "pants1"


def test_clothes_full_body_empty_pool_falls_back_to_separates():
    macro = _macro(0.5, 0.0, _NO_RACE)
    section = _clothes(
        full_body=_slot(chance=100, include_any="suit"),
        upper_body=_slot(chance=100, include_any="shirt"),
        lower_body=_slot(chance=100, include_any="pants"))
    # No suit is installed, so the full body flip fires with an empty pool.
    results = RandomizationService.pick_random_clothes(section, macro, _cc("shirt1", "pants1"), random.Random(0))
    assert _picked(results, "full_body") is None
    assert _warning(results, "full_body") == "full_body_empty_fallback"
    assert _picked(results, "upper_body") == "shirt1", "the character falls back to separates"
    assert _picked(results, "lower_body") == "pants1"


def test_clothes_asset_is_picked_for_only_one_slot():
    macro = _macro(0.5, 0.0, _NO_RACE)
    # One garment matches both slots' keywords; it must not be attached twice.
    section = _clothes(
        accessories=_slot(chance=100, include_any="combo"),
        head=_slot(chance=100, include_any="combo"))
    results = RandomizationService.pick_random_clothes(section, macro, _cc("combo"), random.Random(0))
    attached = [_picked(results, "accessories"), _picked(results, "head")]
    assert attached.count("combo") == 1, "a shared asset is only picked once per character"
    assert None in attached


def test_clothes_changing_one_slot_does_not_shift_another():
    macro = _macro(0.5, 0.0, _NO_RACE)
    cands = _cc("hat1", "hat2", "glasses1", "glasses2", "glasses3")
    # accessories is drawn before head; changing its filter changes its own pick but, because
    # each enabled slot consumes a fixed two draws, must not shift head's pick for a seed.
    base = _clothes(accessories=_slot(include_any="glasses"), head=_slot(include_any="hat"))
    changed = _clothes(accessories=_slot(include_any="glasses", exclude="glasses1"), head=_slot(include_any="hat"))
    for seed in range(20):
        first = RandomizationService.pick_random_clothes(base, macro, cands, random.Random(seed))
        second = RandomizationService.pick_random_clothes(changed, macro, cands, random.Random(seed))
        assert _picked(first, "head") == _picked(second, "head"), "head is unaffected by accessories' filter"


def test_clothes_pick_is_independent_of_candidate_order():
    macro = _macro(0.5, 0.0, _NO_RACE)
    section = _clothes(head=_slot(include_any="hat"))
    cands = _cc("hat_a", "hat_b", "hat_c", "hat_d")
    original = RandomizationService.pick_random_clothes(section, macro, list(cands), random.Random(7))
    shuffled = list(cands)
    random.Random(99).shuffle(shuffled)
    reshuffled = RandomizationService.pick_random_clothes(section, macro, shuffled, random.Random(7))
    assert _picked(original, "head") == _picked(reshuffled, "head"), "the pick is independent of candidate order"


def test_v3_spec_deserializes_with_clothes_disabled():
    # Simulate a version-3 preset: assets exist but there is no clothes section.
    spec = _spec()
    spec["version"] = 3
    del spec["assets"]["clothes"]
    text = RandomizationService.serialize_spec_to_json_string(spec)
    restored = RandomizationService.deserialize_spec_from_json_string(text)
    macro = _macro(0.5, 0.0, _NO_RACE)
    rng = random.Random(0)
    results = RandomizationService.pick_random_clothes(restored["assets"].get("clothes") or {}, macro, _cc("hat1"), rng)
    assert results == [], "a preset without a clothes section adds no clothes"
    assert rng.random() == random.Random(0).random(), "and consumes no draws"
