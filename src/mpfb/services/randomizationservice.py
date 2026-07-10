"""
Module for randomizing human characteristics.

This service concentrates all core randomization logic for the "random human" feature
(which is available under "new human"). The intent is to be able to produce a
human with randomized features from a single operator invocation.

The core functions in this module are deliberately pure: they do not touch any bpy
objects and they never use the global "random" module state. Instead a caller-supplied
"random.Random" instance is threaded through every draw. This keeps the sampling
reproducible (the same seed and the same spec always produce the same result) and cheap
enough to be called in a loop when batch randomization is added later.

The canonical phenotype representation is the "macro info dict" produced by
TargetService, for example:

    { "gender":0.5, "age":0.5, "muscle":0.5, "weight":0.5, "proportions":0.5,
      "height":0.5, "cupsize":0.5, "firmness":0.5,
      "race": {"asian":0.33, "caucasian":0.33, "african":0.33} }

A "randomization spec" is a plain nested dict which is also what gets saved as a preset.
It has a top-level "version" field and named sections, so later sub-features can add
sibling sections ("creation", "details", "assets", "batch") without breaking older presets.
"""

import json, math, random
from .logservice import LogService
from .targetservice import TargetService

_LOG = LogService.get_logger("services.randomizationservice")

# The current version of the randomization spec / preset format. Bump this if the format
# changes in a way that older presets need migrating.
_SPEC_VERSION: int = 4

# Built-in neutral and deviation used when nothing else is specified for an attribute.
_DEFAULT_NEUTRAL: float = 0.5
_DEFAULT_DEVIATION: float = 0.5
_DEFAULT_DISTRIBUTION: str = "bell"

# The scalar phenotype attributes which can be sampled along a continuous scale.
_SCALAR_ATTRIBUTES: list[str] = ["gender", "age", "muscle", "weight", "height", "proportions", "cupsize", "firmness"]

# The three correlated race weights.
_RACES: list[str] = ["asian", "caucasian", "african"]

# The default "assets.skin" section. Skin randomization is on with all three phenotype
# filters and the fallback relaxation enabled, no pack or include filter, and an exclude
# filter that drops the painted-on clothing textures in the system pack. The skin_type and
# material_instances mirror the asset library defaults so the same preset reproduces the
# same material.
_DEFAULT_SKIN_ASSET: dict = {
    "enabled": True,
    "match_gender": True,
    "match_age": True,
    "match_race": True,
    "fallback": True,
    "pack": "",
    "include": "",
    "exclude": "special_suit",
    "skin_type": "MAKESKIN",
    "material_instances": True
    }

# The default section for a plain randomized bodypart type (eyebrows, eyelashes, teeth,
# tongue). Randomization is on with empty pack/include/exclude filters. There is no
# phenotype analog of the skin's match filters for these types, since no installed bodypart
# assets carry age or race labels in their names.
_DEFAULT_BODYPART_ASSET: dict = {
    "enabled": True,
    "pack": "",
    "include": "",
    "exclude": ""
    }

# The default "assets.hair" section. Hair is a plain bodypart type with the same pack /
# include / exclude filters, plus an optional gender filter (off by default, since
# gender-labeled hair styles are few), a relax toggle that drops only the gender filter, and
# an alternative-material randomization toggle (off by default).
_DEFAULT_HAIR_ASSET: dict = {
    "enabled": True,
    "match_gender": False,
    "fallback": True,
    "pack": "",
    "include": "",
    "exclude": "",
    "randomize_alt_materials": False
    }

# The default "assets.eyes" section. Eyes are a special case: rather than a randomized pool
# they are a drop-down over the two installed eye sets (mapped to hardcoded asset paths). The
# mode is one of "DONOTADD", "HIGHPOLY" or "LOWPOLY" (matching the eyes_mode enum ids). The
# material type mirrors the asset library's eyes_type, and alternative-material (iris color)
# randomization is on by default.
_DEFAULT_EYES_ASSET: dict = {
    "mode": "LOWPOLY",
    "material_type": "MAKESKIN",
    "randomize_alt_materials": True
    }

# The plain randomized bodypart types (those with only pack / include / exclude filters).
# Eyes and hair are handled separately because they carry extra settings.
_PLAIN_BODYPART_TYPES: list[str] = ["eyebrows", "eyelashes", "teeth", "tongue"]

# All bodypart types in the fixed order the operator draws them (alphabetical, matching the
# asset subdir names). Keeping the order here makes it the single source of truth, so a seed
# reproduces the same picks regardless of how the UI or operator iterate.
_BODYPART_TYPES: list[str] = ["eyebrows", "eyelashes", "eyes", "hair", "teeth", "tongue"]

# The default section for a clothes slot. Unlike bodyparts, clothes have a per-slot chance
# (how often the slot produces a garment) and split their include filter into a common list
# and two gendered lists; the character's gender (binary split at 0.5) decides which gendered
# list is unioned with the common one. Empty include lists never mean "all clothes": with no
# pack term either the slot pool is empty. The exclude list applies regardless of gender.
_DEFAULT_CLOTHES_SLOT: dict = {
    "enabled": False,
    "chance": 100,
    "pack": "",
    "include_any": "",
    "include_female": "",
    "include_male": "",
    "exclude": ""
    }

# The eight clothes slots, in body order (the order the UI lays them out). Each entry carries
# the slot's default enablement, chance and include keyword lists; a fresh copy merged over
# _DEFAULT_CLOTHES_SLOT gives the slot's default section. The default enablement is "casual
# everyday": full body, upper body, lower body and feet on; head, hands, underwear and
# accessories off. The keyword lists are the initial curated mapping (plain name-substring
# matching); short keywords are avoided since they match greedily ("tie" inside "panties").
_CLOTHES_SLOTS: list[tuple[str, dict]] = [
    ("head", {
        "enabled": False, "chance": 20,
        "include_any": "hat,cap,helmet,beanie,beret,hood,turban"}),
    ("full_body", {
        "enabled": True, "chance": 25,
        "include_any": "suit,uniform,overall,jumpsuit,robe,armor,armour,kimono,tunic",
        "include_female": "dress,gown"}),
    ("upper_body", {
        "enabled": True, "chance": 100,
        "include_any": "shirt,sweater,hoodie,jacket,vest,pullover,cardigan,coat,top",
        "include_female": "blouse"}),
    ("lower_body", {
        "enabled": True, "chance": 100,
        "include_any": "pants,jeans,shorts,trousers,slacks,leggings",
        "include_female": "skirt"}),
    ("hands", {
        "enabled": False, "chance": 10,
        "include_any": "glove,mitten"}),
    ("feet", {
        "enabled": True, "chance": 100,
        "include_any": "shoe,boot,sandal,sneaker,trainer,sock,slipper,loafer",
        "include_female": "heel"}),
    ("underwear", {
        "enabled": False, "chance": 100,
        "include_any": "underwear,swimsuit",
        "include_female": "bra,panties,bikini,lingerie",
        "include_male": "boxers,briefs,trunks"}),
    ("accessories", {
        "enabled": False, "chance": 20,
        "include_any": "glasses,necklace,bracelet,earring,watch,scarf,belt,backpack,bag"})
    ]

# The fixed order clothes slots are drawn in, the single source of truth for reproducibility.
# Full body is drawn first so its coin-flip outcome can gate the upper-body and lower-body
# slots; the remaining slots follow alphabetically. Each enabled slot consumes exactly one
# chance draw and one pick draw regardless of outcome, so changing one slot's settings never
# shifts another slot's result for a given seed.
_CLOTHES_DRAW_ORDER: list[str] = [
    "full_body", "accessories", "feet", "hands", "head", "lower_body", "underwear", "upper_body"]

# The discrete gender values, keyed by the value name used in the "allowed" list. In discrete
# mode a value is picked uniformly among the allowed keys.
_GENDER_VALUES: dict[str, float] = {"female": 0.0, "male": 1.0}

# The four canonical age anchors (baby, child, young, old), keyed by the value name used in the
# "allowed" list. These match the discrete age values used by the "create human" operator.
_AGE_VALUES: dict[str, float] = {"baby": 0.0, "child": 0.1875, "young": 0.5, "old": 1.0}

# Breast attributes are only randomized when the age is at or above this threshold (the
# "young" anchor). This is not (only) because of being prudish, but because there aren't
# any relevant phenotype combinatory macro targets available for younger ages.
_YOUNG_ADULT_THRESHOLD: float = 0.5

# Gender label bands, used only when describing a generated character. Below the female
# max the label is "female", above the male min it is "male" and in between it is "neutral".
# These bands are display-only and do not affect any randomization logic.
_GENDER_FEMALE_MAX: float = 0.4
_GENDER_MALE_MIN: float = 0.6

# The five age bands used when matching a skin asset against the randomized age. Unlike the
# four age anchors above (which drive sampling), these include a dedicated "middleage" band
# because the system skins use "middleage" in their names, which is not an age anchor. Each
# entry is an upper bound; a value below the bound gets that label. Anything at or above the
# last bound falls through to "old", so middleage occupies roughly 0.65 - 0.85.
_SKIN_AGE_BANDS: list[tuple[str, float]] = [("baby", 0.09), ("child", 0.34), ("young", 0.65), ("middleage", 0.85)]

# When matching a skin name against a phenotype label, a couple of labels are substrings of
# a longer label ("male" inside "female", "asian" inside "caucasian"). Testing for the short
# label would then wrongly match a name carrying the long one. The superstring is stripped
# from the name before the short label is tested; see _name_contains_label.
_LABEL_SUPERSTRINGS: dict[str, str] = {"male": "female", "asian": "caucasian"}


class RandomizationService:
    """Service with static methods for randomizing human characteristics. All methods are
    static; the class should never be instantiated."""

    def __init__(self) -> None:
        raise RuntimeError("You should not instance RandomizationService. Use its static methods instead.")

    @staticmethod
    def get_default_phenotype_spec() -> dict:
        """
        Get the built-in randomization spec.

        The returned spec includes all attributes, uses the built-in neutral for each,
        a moderate default deviation and a bell distribution. Gender is discrete by
        default (discrete_gender on); race and age are continuous (their toggles off).

        Returns:
            dict: A fresh randomization spec dict.
        """
        attributes = {}
        for name in _SCALAR_ATTRIBUTES:
            attributes[name] = {
                "include": True,
                "neutral": _DEFAULT_NEUTRAL,
                "deviation": _DEFAULT_DEVIATION
                }
        # Attributes with a discrete mode carry an "allowed" list of the value names that may be
        # picked in that mode. An empty list means the attribute is treated as excluded.
        attributes["gender"]["allowed"] = list(_GENDER_VALUES.keys())
        attributes["age"]["allowed"] = list(_AGE_VALUES.keys())
        attributes["race"] = {"include": True, "allowed": list(_RACES)}
        return {
            "version": _SPEC_VERSION,
            "phenotype": {
                "distribution": _DEFAULT_DISTRIBUTION,
                "discrete_race": False,
                "discrete_gender": True,
                "discrete_age": False,
                "attributes": attributes
                },
            "assets": {
                "asset_material_type": "MAKESKIN",
                "skin": dict(_DEFAULT_SKIN_ASSET),
                "eyes": dict(_DEFAULT_EYES_ASSET),
                "hair": dict(_DEFAULT_HAIR_ASSET),
                "eyebrows": dict(_DEFAULT_BODYPART_ASSET),
                "eyelashes": dict(_DEFAULT_BODYPART_ASSET),
                "teeth": dict(_DEFAULT_BODYPART_ASSET),
                "tongue": dict(_DEFAULT_BODYPART_ASSET),
                "clothes": {slot: _default_clothes_slot(slot) for slot, _ in _CLOTHES_SLOTS}
                }
            }

    @staticmethod
    def get_discrete_value_names(attribute: str) -> list[str]:
        """
        Get the canonical value names for an attribute which has a discrete mode.

        The names are the keys used in an attribute's "allowed" list, returned in the order
        the values are defined. This is the authoritative source for the value names so that
        callers (such as the UI) do not have to duplicate them.

        Args:
            attribute (str): One of "gender", "age" or "race".

        Returns:
            list: The ordered value names for the attribute.
        """
        if attribute == "gender":
            return list(_GENDER_VALUES.keys())
        if attribute == "age":
            return list(_AGE_VALUES.keys())
        if attribute == "race":
            return list(_RACES)
        raise ValueError("Unknown discrete attribute: " + str(attribute))

    @staticmethod
    def sample_value(distribution: str, neutral: float, max_deviation: float, rng: random.Random) -> float:
        """
        Draw a single clamped value for one attribute.

        The value is drawn from the requested probability distribution centered on the
        neutral value, then clamped first to the deviation range and then to the full
        range (0.0 - 1.0). All clamping happens here so that call sites do not have to
        repeat it.

        Args:
            distribution (str): One of "flat", "bell", "pyramid" or "peak".
            neutral (float): The value the distribution is centered on.
            max_deviation (float): The one-sided maximum distance from the neutral value.
            rng (random.Random): The random generator instance to draw from.

        Returns:
            float: A value in the range 0.0 - 1.0.
        """
        low = neutral - max_deviation
        high = neutral + max_deviation

        if max_deviation <= 0.0:
            value = neutral
        elif distribution == "flat":
            value = rng.uniform(low, high)
        elif distribution == "pyramid":
            value = rng.triangular(low, high, neutral)
        elif distribution == "peak":
            # Laplace distribution via inverse CDF. A tight scale gives a strong peak.
            u = rng.random() - 0.5
            scale = max_deviation / 4.0
            value = neutral - scale * _sign(u) * math.log(1.0 - 2.0 * abs(u))
        else:
            if distribution != "bell":
                _LOG.warn("Unknown distribution, falling back to bell", distribution)
            # ~99.7% of a normal distribution lies within three standard deviations.
            value = neutral + rng.gauss(0.0, max_deviation / 3.0)

        value = _clamp(value, low, high)
        return _clamp(value, 0.0, 1.0)

    @staticmethod
    def randomize_macro_info_dict(spec: dict, rng: random.Random) -> dict:
        """
        Produce a randomized macro info dict from a randomization spec.

        This is a pure function: it does not touch any bpy objects, and it only draws from
        the supplied random generator. The result has the same shape as
        TargetService.get_default_macro_info_dict() and can be passed straight to
        HumanService.create_human(macro_detail_dict=...).

        Args:
            spec (dict): A randomization spec, as produced by get_default_phenotype_spec().
            rng (random.Random): The random generator instance to draw from.

        Returns:
            dict: A macro info dict with randomized values.
        """
        phenotype = spec.get("phenotype") or RandomizationService.get_default_phenotype_spec()["phenotype"]
        distribution = phenotype.get("distribution", _DEFAULT_DISTRIBUTION)
        attributes = phenotype.get("attributes", {})

        macro = TargetService.get_default_macro_info_dict()

        # Simple scalar attributes.
        for name in ["muscle", "weight", "height", "proportions"]:
            macro[name] = _resolve_scalar(attributes.get(name, {}), distribution, rng)

        # Gender is discrete by default, continuous when the discrete toggle is off.
        gender_cfg = attributes.get("gender", {})
        gender_neutral = gender_cfg.get("neutral", _DEFAULT_NEUTRAL)
        if not gender_cfg.get("include", True):
            gender = gender_neutral
        elif phenotype.get("discrete_gender", True):
            # Discrete: a value picked uniformly among the allowed ones (female 0.0 / male 1.0).
            # With no value allowed the attribute is treated as excluded, i.e. set to neutral.
            allowed = _filter_allowed(gender_cfg.get("allowed"), _GENDER_VALUES)
            gender = _GENDER_VALUES[rng.choice(allowed)] if allowed else gender_neutral
        else:
            gender = RandomizationService.sample_value(distribution, gender_neutral, gender_cfg.get("deviation", _DEFAULT_DEVIATION), rng)
        macro["gender"] = gender

        # Age is continuous by default, discrete (one of the four anchors) when toggled.
        age_cfg = attributes.get("age", {})
        age_neutral = age_cfg.get("neutral", _DEFAULT_NEUTRAL)
        if not age_cfg.get("include", True):
            age = age_neutral
        elif phenotype.get("discrete_age", False):
            # Discrete: one of the allowed anchors, picked uniformly. With no value allowed the
            # attribute is treated as excluded, i.e. set to neutral.
            allowed = _filter_allowed(age_cfg.get("allowed"), _AGE_VALUES)
            age = _AGE_VALUES[rng.choice(allowed)] if allowed else age_neutral
        else:
            age = RandomizationService.sample_value(distribution, age_neutral, age_cfg.get("deviation", _DEFAULT_DEVIATION), rng)
        macro["age"] = age

        # Race is continuous (independent draws, then normalized) by default, or a discrete
        # pick of exactly one race when the discrete race toggle is enabled.
        macro["race"] = _resolve_race(attributes.get("race", {}), phenotype.get("discrete_race", False), rng)

        # Breast constraint: cupsize and firmness are only randomized when the gender falls
        # on the female side and the age is above the young-adult threshold. Otherwise they
        # are forced to their neutral value regardless of their include flag.
        cupsize_cfg = attributes.get("cupsize", {})
        firmness_cfg = attributes.get("firmness", {})
        if gender < 0.5 and age >= _YOUNG_ADULT_THRESHOLD:
            macro["cupsize"] = _resolve_scalar(cupsize_cfg, distribution, rng)
            macro["firmness"] = _resolve_scalar(firmness_cfg, distribution, rng)
        else:
            macro["cupsize"] = cupsize_cfg.get("neutral", _DEFAULT_NEUTRAL)
            macro["firmness"] = firmness_cfg.get("neutral", _DEFAULT_NEUTRAL)

        return macro

    @staticmethod
    def describe_macro_info_dict(macro: dict, seed: int) -> str:
        """
        Produce a one-line human-readable summary of a generated character.

        This is used for the "create random human" operator's info report. It resolves
        display labels from the generated values: the age label is the closest age anchor,
        the gender label is female/neutral/male by the display-only gender bands, and the
        race label is the race whose weight is above 0.5 (or "mixed race" if none is). The
        race weights are listed in african/asian/caucasian order.

        Args:
            macro (dict): A macro info dict as produced by randomize_macro_info_dict().
            seed (int): The seed the character was generated with.

        Returns:
            str: For example "Generated with seed 123: A young (0.6) caucasian (0.0/0.0/1.0) female (0.1)".
        """
        age = macro["age"]
        gender = macro["gender"]
        race = macro["race"]

        # Age label: whichever anchor the sampled value ends up closest to.
        age_label = min(_AGE_VALUES, key=lambda name: abs(age - _AGE_VALUES[name]))

        # Gender label: female below the female max, male above the male min, neutral between.
        if gender < _GENDER_FEMALE_MAX:
            gender_label = "female"
        elif gender > _GENDER_MALE_MIN:
            gender_label = "male"
        else:
            gender_label = "neutral"

        # Race label: the single race above 0.5, or "mixed race" when the weights are spread out.
        race_label = "mixed race"
        for name in _RACES:
            if race.get(name, 0.0) > 0.5:
                race_label = name
                break

        article = "An" if age_label[0] in "aeiou" else "A"
        race_values = "/".join(_fmt(race.get(name, 0.0)) for name in ["african", "asian", "caucasian"])

        return (
            "Generated with seed " + str(seed) + ": " + article + " " +
            age_label + " (" + _fmt(age) + ") " +
            race_label + " (" + race_values + ") " +
            gender_label + " (" + _fmt(gender) + ")"
            )

    @staticmethod
    def get_default_skin_asset_spec() -> dict:
        """Get a fresh copy of the default "assets.skin" section."""
        return dict(_DEFAULT_SKIN_ASSET)

    @staticmethod
    def get_bodypart_types() -> list[str]:
        """
        Get the bodypart types in the fixed order they are drawn in.

        The order (alphabetical, matching the asset subdir names) is the single source of
        truth for both the UI and the operator, so a seed reproduces the same picks. Note
        "eyes" is included even though it is picked from a drop-down rather than a pool.

        Returns:
            list: ["eyebrows", "eyelashes", "eyes", "hair", "teeth", "tongue"].
        """
        return list(_BODYPART_TYPES)

    @staticmethod
    def get_plain_bodypart_types() -> list[str]:
        """
        Get the plain randomized bodypart types (only pack / include / exclude filters).

        These are the types with no extra settings, i.e. all of get_bodypart_types() except
        the special "eyes" and "hair".

        Returns:
            list: ["eyebrows", "eyelashes", "teeth", "tongue"].
        """
        return list(_PLAIN_BODYPART_TYPES)

    @staticmethod
    def get_default_bodypart_asset_spec(bodypart: str) -> dict:
        """
        Get a fresh copy of the default "assets.<bodypart>" section.

        Args:
            bodypart (str): One of the values returned by get_bodypart_types().

        Returns:
            dict: The default section for that bodypart type.
        """
        if bodypart == "eyes":
            return dict(_DEFAULT_EYES_ASSET)
        if bodypart == "hair":
            return dict(_DEFAULT_HAIR_ASSET)
        if bodypart in _PLAIN_BODYPART_TYPES:
            return dict(_DEFAULT_BODYPART_ASSET)
        raise ValueError("Unknown bodypart type: " + str(bodypart))

    @staticmethod
    def get_clothes_slots() -> list[str]:
        """
        Get the clothes slot names in body order (the order the UI lays them out).

        This is the canonical slot list; the UI supplies only the display labels. Note the
        rng draw order is different (full body first, then alphabetical) and lives in
        pick_random_clothes, so the UI order does not affect reproducibility.

        Returns:
            list: ["head", "full_body", "upper_body", "lower_body", "hands", "feet",
            "underwear", "accessories"].
        """
        return [slot for slot, _ in _CLOTHES_SLOTS]

    @staticmethod
    def get_default_clothes_asset_spec(slot: str) -> dict:
        """
        Get a fresh copy of the default "assets.clothes.<slot>" section.

        Args:
            slot (str): One of the values returned by get_clothes_slots().

        Returns:
            dict: The default section for that clothes slot.
        """
        return _default_clothes_slot(slot)

    @staticmethod
    def skin_gender_label(macro: dict) -> str:
        """
        Get the gender label used when matching a skin asset against the randomized gender.

        This is a binary split at 0.5 ("female" below, "male" at or above), deliberately
        unlike the three-band display labels used by describe_macro_info_dict.

        Args:
            macro (dict): A macro info dict as produced by randomize_macro_info_dict().

        Returns:
            str: "female" or "male".
        """
        return "female" if macro["gender"] < 0.5 else "male"

    @staticmethod
    def skin_age_label(macro: dict) -> str:
        """
        Get the age label used when matching a skin asset against the randomized age.

        The value is placed in one of five bands (baby, child, young, middleage, old). The
        middleage band exists because the system skins use "middleage" in their names.

        Args:
            macro (dict): A macro info dict as produced by randomize_macro_info_dict().

        Returns:
            str: One of "baby", "child", "young", "middleage" or "old".
        """
        age = macro["age"]
        for label, upper in _SKIN_AGE_BANDS:
            if age < upper:
                return label
        return "old"

    @staticmethod
    def skin_race_label(macro: dict) -> str | None:
        """
        Get the race label used when matching a skin asset against the randomized race.

        Returns the race whose weight is above 0.5, or None when no race dominates (a
        mixed-race character); the race filter is then skipped for that character.

        Args:
            macro (dict): A macro info dict as produced by randomize_macro_info_dict().

        Returns:
            str | None: "asian", "caucasian", "african" or None.
        """
        race = macro.get("race", {})
        for name in _RACES:
            if race.get(name, 0.0) > 0.5:
                return name
        return None

    @staticmethod
    def pick_random_skin(spec: dict, macro: dict, candidates: list[dict], rng: random.Random) -> dict | None:
        """
        Pick one skin asset from a list of candidates according to the spec's skin section.

        This is a pure function: it takes the candidate list as plain data (the caller
        discovers the installed skins), so it needs no bpy objects or installed assets and
        is fully unit-testable. The candidate list is sorted by name before drawing, so the
        pick only depends on the seed, the spec and the set of candidates, never on the
        order they were discovered in.

        The pack, include and exclude filters express hard user intent and are always
        applied. The three phenotype filters (gender, age, race) narrow the pool further;
        when the pool is empty and the fallback toggle is on, they are dropped one at a time
        in the order age, then race, then gender, until the pool is non-empty.

        Args:
            spec (dict): A randomization spec; its "assets"/"skin" section is read.
            macro (dict): The randomized macro info dict, used to resolve the phenotype labels.
            candidates (list): Candidate dicts with "name", "path" and "pack" (or None) keys.
            rng (random.Random): The random generator instance to draw from.

        Returns:
            dict | None: The chosen candidate, or None when skin randomization is disabled,
            there are no candidates, or nothing matches (even after fallback).
        """
        skin = (spec.get("assets") or {}).get("skin") or {}
        if not skin.get("enabled", False) or not candidates:
            return None

        # Phenotype filters, each keyed by its relaxation name. A filter is only present when
        # it is enabled in the spec and yields a label (race yields none for a mixed-race
        # character), so a filter missing from this dict is simply off.
        labels: dict[str, str] = {}
        if skin.get("match_gender", True):
            labels["gender"] = RandomizationService.skin_gender_label(macro)
        if skin.get("match_age", True):
            labels["age"] = RandomizationService.skin_age_label(macro)
        if skin.get("match_race", True):
            race_label = RandomizationService.skin_race_label(macro)
            if race_label is not None:
                labels["race"] = race_label

        # Age relaxes first because it is the most restrictive in practice, then race, then
        # gender. Pack, include and exclude are hard filters and never relaxed.
        return _filter_and_pick_candidates(skin, candidates, rng, labels, ["age", "race", "gender"])

    @staticmethod
    def pick_random_bodypart(spec_section: dict, macro: dict, candidates: list[dict], rng: random.Random) -> dict | None:
        """
        Pick one bodypart asset from a list of candidates according to a bodypart section.

        This is a pure function, like pick_random_skin, sharing the same filter-and-pick
        logic. The pack, include and exclude filters express hard user intent and are always
        applied. Hair additionally has an optional gender filter (its "match_gender" toggle);
        when the gender-filtered pool is empty and the section's "fallback" toggle is on,
        only the gender filter is dropped and the pick retried (pack, include and exclude are
        never relaxed). The other bodypart types have no phenotype filter.

        Args:
            spec_section (dict): One "assets.<bodypart>" section (hair or a plain type).
            macro (dict): The randomized macro info dict, used to resolve the gender label.
            candidates (list): Candidate dicts with "name", "path" and "pack" (or None) keys.
            rng (random.Random): The random generator instance to draw from.

        Returns:
            dict | None: The chosen candidate, or None when the type is disabled, there are
            no candidates, or nothing matches (even after fallback).
        """
        section = spec_section or {}
        if not section.get("enabled", False) or not candidates:
            return None

        # Only hair carries a phenotype filter; a missing "match_gender" key means off.
        labels: dict[str, str] = {}
        if section.get("match_gender", False):
            labels["gender"] = RandomizationService.skin_gender_label(macro)

        return _filter_and_pick_candidates(section, candidates, rng, labels, ["gender"])

    @staticmethod
    def pick_random_clothes(clothes_section: dict, macro: dict, candidates: list[dict],
                            rng: random.Random) -> list[dict]:
        """
        Pick at most one clothes asset per enabled slot from a list of candidates.

        This is a pure function, like the other pick methods, but it drives all eight clothes
        slots in one call so it can enforce the full-body exclusivity and the strict draw
        accounting. The slots are processed in a fixed order (full body first so its outcome
        can gate the upper and lower body slots, then the rest alphabetically). Each enabled
        slot consumes exactly one chance draw and one pick draw, in that order, regardless of
        whether it fires, is suppressed or has an empty pool; disabled slots consume none. So
        changing one slot's chance or filters never shifts another slot's result for a seed.

        For each slot the pool is the candidates whose name matches the common include list or
        the gendered include list applicable to the character's gender (binary split at 0.5),
        minus the exclude matches, intersected with the pack filter. Empty include lists never
        select all clothes: with no pack term either the pool is empty and the slot is skipped.
        An asset picked for an earlier slot is removed from later slots' pools. When the full
        body slot fires and attaches a garment, the upper and lower body slots are suppressed.

        Args:
            clothes_section (dict): The "assets.clothes" section (slot name -> slot section).
            macro (dict): The randomized macro info dict, used to resolve the gender label.
            candidates (list): Candidate dicts with "name", "path" and "pack" (or None) keys.
            rng (random.Random): The random generator instance to draw from.

        Returns:
            list: One dict per enabled slot, in draw order, with keys "slot", "pick" (the
            chosen candidate or None) and "warning" (None, "empty_pool" when a non-full-body
            slot fired with an empty pool, or "full_body_empty_fallback" when the full body
            slot fired with an empty pool and the character falls back to separates).
        """
        clothes = clothes_section or {}
        gender_label = RandomizationService.skin_gender_label(macro)

        picked_names: set = set()
        full_body_attached = False
        results: list[dict] = []

        for slot in _CLOTHES_DRAW_ORDER:
            section = clothes.get(slot) or {}
            if not section.get("enabled", False):
                continue

            # Two draws per enabled slot, always consumed and always in this order.
            chance_roll = rng.random()
            pick_roll = rng.random()

            suppressed = full_body_attached and slot in ("upper_body", "lower_body")
            fires = (chance_roll < float(section.get("chance", 0)) / 100.0) and not suppressed

            pick = None
            warning = None
            if fires:
                # The common include list unioned with the gendered list for this character.
                gendered = section.get("include_female" if gender_label == "female" else "include_male", "")
                parts = [part for part in [section.get("include_any", ""), gendered] if part and str(part).strip()]
                combined_include = ",".join(parts)
                pack = str(section.get("pack", "")).strip()

                if not _split_keywords(combined_include) and not pack:
                    # An unmapped slot with no pack term never picks arbitrary garments.
                    pool: list[dict] = []
                else:
                    synthesized = {"pack": pack, "include": combined_include, "exclude": section.get("exclude", "")}
                    pool = _filter_candidates(synthesized, candidates, {}, [])
                    pool = [candidate for candidate in pool if candidate.get("name") not in picked_names]

                if pool:
                    pick = pool[int(pick_roll * len(pool))]
                    picked_names.add(pick.get("name"))
                    if slot == "full_body":
                        full_body_attached = True
                elif slot == "full_body":
                    warning = "full_body_empty_fallback"
                else:
                    warning = "empty_pool"

            results.append({"slot": slot, "pick": pick, "warning": warning})

        return results

    @staticmethod
    def pick_random_alternative_material(default_name: str, alternatives: list[str], rng: random.Random) -> str:
        """
        Pick one material name uniformly from a default plus its alternatives.

        Used for the eyes / hair alternative-material randomization. The default and the
        alternatives are combined, de-duplicated (the eyes discovery can yield duplicates)
        and sorted by name before drawing, so the pick only depends on the seed and the set
        of names. When there are no distinct alternatives the default is returned without
        drawing from rng, so an asset with no alternatives does not shift the seed for later
        draws.

        Args:
            default_name (str): The asset's default material name.
            alternatives (list): The alternative material names (may contain duplicates or
                the default; they are de-duplicated together with the default).
            rng (random.Random): The random generator instance to draw from.

        Returns:
            str: The chosen material name (the default when there are no alternatives).
        """
        unique: list[str] = []
        seen: set = set()
        for name in [default_name] + list(alternatives or []):
            if name is not None and name not in seen:
                seen.add(name)
                unique.append(name)
        if len(unique) <= 1:
            return default_name
        unique.sort(key=lambda value: str(value).lower())
        return rng.choice(unique)

    @staticmethod
    def serialize_spec_to_json_string(spec: dict) -> str:
        """Serialize a randomization spec to a JSON string."""
        return json.dumps(spec, indent=4, sort_keys=True)

    @staticmethod
    def deserialize_spec_from_json_string(json_string: str) -> dict:
        """
        Deserialize a randomization spec from a JSON string.

        Unknown sibling sections are preserved untouched, so presets written by later
        sub-features can still be read here.
        """
        spec = json.loads(json_string)
        if "version" not in spec:
            _LOG.warn("Randomization spec has no version field", spec)
        return spec

    @staticmethod
    def serialize_spec_to_json_file(spec: dict, file_path: str) -> None:
        """Serialize a randomization spec to a JSON file."""
        with open(file_path, "w") as json_file:
            json_file.write(RandomizationService.serialize_spec_to_json_string(spec))

    @staticmethod
    def deserialize_spec_from_json_file(file_path: str) -> dict:
        """Deserialize a randomization spec from a JSON file."""
        with open(file_path, "r") as json_file:
            return RandomizationService.deserialize_spec_from_json_string(json_file.read())


def _sign(value: float) -> float:
    """Return -1.0 for negative values, 1.0 otherwise."""
    return -1.0 if value < 0.0 else 1.0


def _fmt(value: float) -> str:
    """Format a value for display, rounded to two decimals (e.g. 0.6, 0.55, 1.0)."""
    return str(round(value, 2))


def _clamp(value: float, low: float, high: float) -> float:
    """Clamp value to the inclusive range [low, high]."""
    if value < low:
        return low
    if value > high:
        return high
    return value


def _resolve_scalar(attribute_cfg: dict, distribution: str, rng: random.Random) -> float:
    """Resolve one scalar attribute: its neutral value if excluded, else a sampled draw."""
    neutral = attribute_cfg.get("neutral", _DEFAULT_NEUTRAL)
    if not attribute_cfg.get("include", True):
        return neutral
    deviation = attribute_cfg.get("deviation", _DEFAULT_DEVIATION)
    return RandomizationService.sample_value(distribution, neutral, deviation, rng)


def _filter_allowed(allowed: list[str] | None, valid_keys: dict[str, float] | list[str]) -> list[str]:
    """Return the requested value names which are valid, or all of them when unspecified.

    A missing (None) "allowed" list defaults to all valid keys, so presets written before the
    "allowed" field existed still randomize over every value. An explicit empty list stays
    empty, which callers treat as "excluded".
    """
    if allowed is None:
        return list(valid_keys)
    return [name for name in allowed if name in valid_keys]


def _default_clothes_slot(slot: str) -> dict:
    """Build a fresh default section for a clothes slot by merging its overrides over the
    shared _DEFAULT_CLOTHES_SLOT template. Raises ValueError for an unknown slot name."""
    for name, overrides in _CLOTHES_SLOTS:
        if name == slot:
            section = dict(_DEFAULT_CLOTHES_SLOT)
            section.update(overrides)
            return section
    raise ValueError("Unknown clothes slot: " + str(slot))


def _split_keywords(value: str) -> list[str]:
    """Split a comma-separated keyword string into a list of lowercased, trimmed keywords.

    Surrounding whitespace is stripped and empty entries (e.g. from a trailing comma) are
    dropped, so a single plain string with no comma behaves as a one-keyword list.
    """
    if not value:
        return []
    return [keyword.strip().lower() for keyword in str(value).split(",") if keyword.strip()]


def _name_contains_label(name: str, label: str) -> bool:
    """Case-insensitively test whether an asset name contains a phenotype label.

    A couple of labels are substrings of a longer label ("male" inside "female", "asian"
    inside "caucasian"); the longer label is removed from the name before the shorter one is
    tested, so for example "male" does not match inside "young_caucasian_female2".
    """
    lowered = str(name).lower()
    label = str(label).lower()
    superstring = _LABEL_SUPERSTRINGS.get(label)
    if superstring:
        lowered = lowered.replace(superstring, "")
    return label in lowered


def _filter_candidates(section: dict, candidates: list[dict],
                       labels: dict[str, str], fallback_order: list[str]) -> list[dict]:
    """Filter a candidate list by an asset section's filters and return the matching pool.

    This is the pure (rng-free) core of the pick helpers. The section supplies the hard pack
    / include / exclude filters (always applied) and the "fallback" toggle. The caller
    resolves the phenotype filters into "labels" (filter name -> label) and gives the order
    they relax in via "fallback_order"; a filter missing from "labels" is simply off.
    Candidates are sorted by name so a later pick is independent of the caller's enumeration
    order. Returns the matching pool (possibly empty), sorted by name.
    """
    # Sort by name so a later draw is independent of the caller's enumeration order.
    pool = sorted(candidates, key=lambda candidate: str(candidate.get("name", "")).lower())

    # Hard filters (pack, include, exclude): applied once and never relaxed.
    pack = str(section.get("pack", "")).strip().lower()
    if pack:
        pool = [c for c in pool if c.get("pack") and pack in str(c["pack"]).lower()]
    include = _split_keywords(section.get("include", ""))
    if include:
        pool = [c for c in pool if any(keyword in str(c.get("name", "")).lower() for keyword in include)]
    exclude = _split_keywords(section.get("exclude", ""))
    if exclude:
        pool = [c for c in pool if not any(keyword in str(c.get("name", "")).lower() for keyword in exclude)]

    active = [name for name in fallback_order if name in labels]

    def _apply(active_filters: list[str]) -> list[dict]:
        result = pool
        for name in active_filters:
            result = [c for c in result if _name_contains_label(c.get("name", ""), labels[name])]
        return result

    matched = _apply(active)
    if not matched and section.get("fallback", True):
        # Drop the label filters one at a time, in the given order, until something matches.
        for name in fallback_order:
            if name in active:
                active.remove(name)
                matched = _apply(active)
                if matched:
                    break

    return matched


def _filter_and_pick_candidates(section: dict, candidates: list[dict], rng: random.Random,
                                labels: dict[str, str], fallback_order: list[str]) -> dict | None:
    """Filter a candidate list by an asset section's filters and pick one at random.

    This is the shared core of pick_random_skin and pick_random_bodypart; the filtering is
    done by _filter_candidates and the single rng draw happens here. Returns the chosen
    candidate, or None when nothing matches (even after fallback).
    """
    matched = _filter_candidates(section, candidates, labels, fallback_order)
    if not matched:
        return None
    return rng.choice(matched)


def _resolve_race(race_cfg: dict, discrete_race: bool, rng: random.Random) -> dict[str, float]:
    """Resolve the three race weights as a nested dict summing to ~1.0."""
    even_mix = {name: 1.0 / len(_RACES) for name in _RACES}
    if not race_cfg.get("include", True):
        return even_mix
    if discrete_race:
        # Discrete: exactly one of the allowed races. With no race allowed this is treated as
        # excluded, i.e. an even mix.
        allowed = _filter_allowed(race_cfg.get("allowed"), _RACES)
        if not allowed:
            return even_mix
        chosen = rng.choice(allowed)
        return {name: (1.0 if name == chosen else 0.0) for name in _RACES}
    weights = {name: rng.random() for name in _RACES}
    total = sum(weights.values())
    if total <= 0.0:
        return even_mix
    return {name: weights[name] / total for name in _RACES}
