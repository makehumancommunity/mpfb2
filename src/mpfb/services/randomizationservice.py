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
_SPEC_VERSION: int = 1

# Built-in neutral and deviation used when nothing else is specified for an attribute.
_DEFAULT_NEUTRAL: float = 0.5
_DEFAULT_DEVIATION: float = 0.5
_DEFAULT_DISTRIBUTION: str = "bell"

# The scalar phenotype attributes which can be sampled along a continuous scale.
_SCALAR_ATTRIBUTES: list[str] = ["gender", "age", "muscle", "weight", "height", "proportions", "cupsize", "firmness"]

# The three correlated race weights.
_RACES: list[str] = ["asian", "caucasian", "african"]

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
