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
It has a top-level "version" field and named sections ("phenotype", "creation", "assets",
"details", "batch").
"""

import json, math, random
from .logservice import LogService
from .targetservice import TargetService

_LOG = LogService.get_logger("services.randomizationservice")

# The current version of the randomization spec / preset format.
_SPEC_VERSION: int = 1

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

# The canonical age anchors, keyed by the value name used in the "allowed" list. Baby, child,
# young and old are the discrete age values used by the "create human" operator; middleage is an
# extra randomization-only anchor sitting at the center of the skin "middleage" band (see
# _SKIN_AGE_BANDS below), so discrete age can land a plausible adult between "young" and "old".
_AGE_VALUES: dict[str, float] = {"baby": 0.0, "child": 0.1875, "young": 0.5, "middleage": 0.75, "old": 1.0}

# The default gender and age cutoffs for the breast constraint (see randomize_macro_info_dict).
# Breast attributes are only randomized when the gender is on the female side of the gender cutoff
# and the age is at or above the age cutoff. The age cutoff is not (only) about being prudish, but
# also because there aren't any relevant phenotype combinatory macro targets available for younger
# ages. Both cutoffs are user-configurable per spec; these are the built-in defaults.
_DEFAULT_BREAST_GENDER_CUTOFF: float = 0.6
_DEFAULT_BREAST_AGE_CUTOFF: float = 0.4

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

# The detail sections which ship disabled (min=max=0). Genital morphs should be opt-in, and the
# breast detail categories are dropped because the Breast shape sub-panel already randomizes the
# cupsize/firmness macros of the same body area.
_DEFAULT_DETAIL_DISABLED_SECTIONS: list[str] = ["breast", "genitals"]

# The built-in per-section detail defaults: a pick count between 0 and 3 and a moderate 0.5 max
# deviation. Disabled sections use min=max=0 instead.
_DEFAULT_DETAIL_MIN: int = 0
_DEFAULT_DETAIL_MAX: int = 3
_DEFAULT_DETAIL_DEVIATION: float = 0.5

# A picked detail category draws its magnitude uniformly in [factor * deviation, deviation], so
# every pick produces a visible change (a plain draw centered on the neutral 0.0 would mostly
# land near zero and be invisible). The sign is a separate 50/50 draw. The global distribution
# setting deliberately does not apply to detail values.
_DETAIL_MAGNITUDE_FLOOR_FACTOR: float = 0.25

# The default "batch" section. Unlike the other sections it carries no "enabled" key: batch
# generation only runs when its own operator is invoked, so there is nothing to gate, and a
# preset without the section loads these defaults rather than a disabled state. The defaults
# lay 10 characters out on a grid one blender unit apart, ten to a row, with a random rotation
# around Z (the crowd-scattering use case). The random-area settings only take effect when the
# strategy is switched to RANDOM.
_DEFAULT_BATCH: dict = {
    "count": 10,
    "strategy": "GRID",
    "origin_x": 0.0,
    "origin_y": 0.0,
    "spacing_x": 1.0,
    "row_length": 10,
    "row_shift_y": 1.0,
    "x_min": -5.0,
    "x_max": 5.0,
    "y_min": -5.0,
    "y_max": 5.0,
    "min_distance": 0.0,
    "random_rotation": True
    }

# The bounded rejection-sampling cap for the RANDOM strategy's minimum-distance constraint. A
# position landing closer than the minimum to an already-placed character is redrawn up to this
# many times; after that the overlap is accepted (and flagged so the operator can warn). This
# keeps an impossible constraint (a tiny area with a large minimum distance) from looping forever.
_BATCH_PLACEMENT_RETRY_CAP: int = 25


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
        a moderate default deviation and a bell distribution. Gender and age are discrete
        by default (discrete_gender / discrete_age on); race is continuous (its toggle off).

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
                "discrete_age": True,
                "breast_gender_cutoff": _DEFAULT_BREAST_GENDER_CUTOFF,
                "breast_age_cutoff": _DEFAULT_BREAST_AGE_CUTOFF,
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

        # Breast constraint: cupsize and firmness are only randomized when the gender falls on
        # the female side of the (configurable) gender cutoff and the age is at or above the
        # (configurable) age cutoff. Otherwise they are forced to their neutral value regardless
        # of their include flag.
        gender_cutoff = phenotype.get("breast_gender_cutoff", _DEFAULT_BREAST_GENDER_CUTOFF)
        age_cutoff = phenotype.get("breast_age_cutoff", _DEFAULT_BREAST_AGE_CUTOFF)
        cupsize_cfg = attributes.get("cupsize", {})
        firmness_cfg = attributes.get("firmness", {})
        if gender < gender_cutoff and age >= age_cutoff:
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
    def get_default_detail_spec(section_names: list[str]) -> dict:
        """
        Build the default "details" section for the given target.json section names.

        Detail randomization is on with symmetry on. Every section gets min 0 / max 3, empty
        include/exclude filters and a 0.5 max deviation, except the canonical disabled sections
        (breast, genitals) which get min=max=0. The caller supplies the section names (derived
        from target.json), so the service stays free of any filesystem or target.json knowledge,
        mirroring the candidates-passed-in pattern used by the asset picks.

        Args:
            section_names (list): The target.json section names to configure (minus "measure").

        Returns:
            dict: A fresh "details" section dict (enabled, symmetry, sections).
        """
        sections: dict = {}
        for name in section_names:
            disabled = name in _DEFAULT_DETAIL_DISABLED_SECTIONS
            sections[name] = {
                "min": 0 if disabled else _DEFAULT_DETAIL_MIN,
                "max": 0 if disabled else _DEFAULT_DETAIL_MAX,
                "include": "",
                "exclude": "",
                "deviation": _DEFAULT_DETAIL_DEVIATION
                }
        return {"enabled": True, "symmetry": True, "sections": sections}

    @staticmethod
    def get_default_batch_spec() -> dict:
        """
        Get a fresh copy of the default "batch" section.

        The section holds the character count, the placement strategy and the grid and
        random-area settings. It has no "enabled" key: batch generation only runs when its
        own operator is invoked (see the module comment on _DEFAULT_BATCH).

        Returns:
            dict: A fresh "batch" section dict.
        """
        return dict(_DEFAULT_BATCH)

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
    def pick_random_details(spec_details: dict, sections: dict, rng: random.Random) -> list[dict]:
        """
        Pick random detail targets and return a flat stack ready for bulk loading.

        This is a pure function, like the asset picks: "sections" is plain data (a dict mapping
        each target.json section name to its list of category dicts, as parsed by the caller),
        so it needs no bpy objects or filesystem access and is fully unit-testable. For each
        section a pick count is drawn uniformly in [min, max] (clamped to the filtered pool
        size), that many distinct categories are picked from the name-sorted pool, and a value
        is drawn per pick. The value is a magnitude uniform in [0.25 * deviation, deviation] with
        a separate 50/50 sign draw selecting the decr ("negative") or incr ("positive") target
        from the category's "opposites" table; a category without opposites is one-sided and only
        ever gets a positive value. The global distribution setting does not apply here.

        Reproducibility depends on a fixed number and order of draws: sections are iterated in
        sorted name order and the pool is sorted by category name before the pick; per pick the
        draws are sign, then value (left before right for an asymmetric sided category). A sided
        category counts as one pick; with symmetry on a single value is mirrored to both sides,
        with symmetry off the two sides get independent draws. Nothing is drawn at all when
        detail randomization is disabled, and a section missing from the spec contributes nothing
        and consumes no draws.

        Args:
            spec_details (dict): The spec's "details" section (None or empty means disabled).
            sections (dict): Section name -> list of category dicts, as parsed from target.json.
            rng (random.Random): The random generator instance to draw from.

        Returns:
            list: A flat list of {"target": name, "value": float} dicts ready for
            TargetService.bulk_load_targets. Empty when detail randomization is disabled.
        """
        details = spec_details or {}
        if not details.get("enabled", False):
            return []

        symmetry = details.get("symmetry", True)
        section_specs = details.get("sections") or {}

        stack: list[dict] = []
        for section_name in sorted(sections.keys()):
            section_cfg = section_specs.get(section_name)
            if not section_cfg:
                # A section missing from the spec is disabled (an older preset, or a section the
                # UI did not write). It contributes nothing and consumes no draws.
                continue

            categories = sorted(sections[section_name] or [], key=lambda category: str(category.get("name", "")).lower())
            pool = _filter_detail_categories(section_cfg, categories)
            picked = _pick_detail_categories(section_cfg, pool, rng)

            deviation = float(section_cfg.get("deviation", _DEFAULT_DETAIL_DEVIATION))
            for category in picked:
                stack.extend(_detail_targets_for_category(category, deviation, symmetry, rng))

        return stack

    @staticmethod
    def derive_character_seeds(base_seed: int, count: int) -> list[int]:
        """
        Derive one per-character seed for each character in a batch.

        A master random.Random(base_seed) draws one seed per character, in order. The seed for
        character i therefore depends only on the base seed and i, not on the batch size: the
        same base seed gives character i the same seed whether the batch is 5 or 50 characters,
        and a character built from its own seed reproduces exactly (the single-character
        operator run with that seed produces the same human). Placement is drawn from a separate
        stream (see compute_batch_placements), so toggling placement never shifts a character.

        Args:
            base_seed (int): The batch's base seed.
            count (int): The number of characters in the batch.

        Returns:
            list: The per-character seeds, one per character, in character order.
        """
        master = random.Random(base_seed)
        return [master.randint(1, 2 ** 31 - 1) for _ in range(count)]

    @staticmethod
    def compute_batch_placements(batch_spec: dict, count: int, rng: random.Random) -> list[dict]:
        """
        Compute the scene placement for each character in a batch.

        The draw order per character is fixed: position first (for the RANDOM strategy, plus any
        minimum-distance retries), then the rotation. The GRID strategy computes its positions
        from the spacing / row length / row shift and consumes no draws for them; the rotation is
        still drawn when random rotation is enabled. Only X and Y are placed (characters stay
        feet-on-ground at z=0); the rotation is around Z.

        For the RANDOM strategy a nonzero minimum distance triggers bounded rejection sampling: a
        position landing closer than the minimum to an already-placed character is redrawn up to
        _BATCH_PLACEMENT_RETRY_CAP times, then accepted with the "overlap" flag set so the caller
        can warn.

        Args:
            batch_spec (dict): The "batch" section (strategy, spacings, area, minimum distance,
                random rotation).
            count (int): The number of characters to place.
            rng (random.Random): The placement rng (kept separate from the per-character seeds).

        Returns:
            list: One dict per character, {"location": (x, y, 0.0), "rotation_z": float,
            "overlap": bool}, in character order.
        """
        strategy = batch_spec.get("strategy", "GRID")
        random_rotation = batch_spec.get("random_rotation", True)

        placements: list[dict] = []
        placed_xy: list[tuple[float, float]] = []
        for index in range(count):
            if strategy == "RANDOM":
                location, overlap = _draw_random_position(batch_spec, placed_xy, rng)
            else:
                location, overlap = _grid_position(batch_spec, index), False
            placed_xy.append((location[0], location[1]))

            rotation_z = rng.uniform(0.0, 2.0 * math.pi) if random_rotation else 0.0
            placements.append({"location": location, "rotation_z": rotation_z, "overlap": overlap})
        return placements

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
        return json.loads(json_string)

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

    A missing (None) "allowed" list defaults to all valid keys. An explicit empty list stays
    empty, which callers treat as "excluded".
    """
    if allowed is None:
        return list(valid_keys)
    return [name for name in allowed if name in valid_keys]


def _grid_position(batch_spec: dict, index: int) -> tuple[float, float, float]:
    """Compute the grid position for the character at the given index (consumes no draws).

    Characters fill a row along X at a fixed spacing; once a row reaches the configured length
    the next character starts a new row, shifted along Y. The first character sits at the
    configured origin (origin_x, origin_y); Z is always 0.0 so the characters stay on the floor.
    Row length is clamped to at least 1 so a zero or negative setting cannot cause a division
    error.
    """
    origin_x = float(batch_spec.get("origin_x", _DEFAULT_BATCH["origin_x"]))
    origin_y = float(batch_spec.get("origin_y", _DEFAULT_BATCH["origin_y"]))
    spacing_x = float(batch_spec.get("spacing_x", _DEFAULT_BATCH["spacing_x"]))
    row_shift_y = float(batch_spec.get("row_shift_y", _DEFAULT_BATCH["row_shift_y"]))
    row_length = max(1, int(batch_spec.get("row_length", _DEFAULT_BATCH["row_length"])))
    column = index % row_length
    row = index // row_length
    return (origin_x + column * spacing_x, origin_y + row * row_shift_y, 0.0)


def _draw_random_position(batch_spec: dict, placed_xy: list[tuple[float, float]],
                          rng: random.Random) -> tuple[tuple[float, float, float], bool]:
    """Draw a random position within the configured rectangle, honoring the minimum distance.

    A first position is always drawn. When a minimum distance is set, the position is redrawn up
    to _BATCH_PLACEMENT_RETRY_CAP times while it lands closer than the minimum to an already
    placed character; if no acceptable position is found within the cap the last one is kept and
    the overlap flag is returned True. Returns the (x, y, 0.0) tuple and the overlap flag.
    """
    x_min = float(batch_spec.get("x_min", _DEFAULT_BATCH["x_min"]))
    x_max = float(batch_spec.get("x_max", _DEFAULT_BATCH["x_max"]))
    y_min = float(batch_spec.get("y_min", _DEFAULT_BATCH["y_min"]))
    y_max = float(batch_spec.get("y_max", _DEFAULT_BATCH["y_max"]))
    min_distance = float(batch_spec.get("min_distance", 0.0))

    x = rng.uniform(x_min, x_max)
    y = rng.uniform(y_min, y_max)
    overlap = False
    if min_distance > 0.0 and placed_xy:
        overlap = not _min_distance_ok(x, y, placed_xy, min_distance)
        for _ in range(_BATCH_PLACEMENT_RETRY_CAP):
            if not overlap:
                break
            x = rng.uniform(x_min, x_max)
            y = rng.uniform(y_min, y_max)
            overlap = not _min_distance_ok(x, y, placed_xy, min_distance)
    return (x, y, 0.0), overlap


def _min_distance_ok(x: float, y: float, placed_xy: list[tuple[float, float]], min_distance: float) -> bool:
    """Return True when (x, y) is at least min_distance from every already-placed position."""
    min_distance_sq = min_distance * min_distance
    for placed_x, placed_y in placed_xy:
        dx = x - placed_x
        dy = y - placed_y
        if dx * dx + dy * dy < min_distance_sq:
            return False
    return True


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


def _filter_detail_categories(section_cfg: dict, categories: list[dict]) -> list[dict]:
    """Filter a section's categories by its include / exclude keyword lists.

    Include keeps a category whose name contains at least one include keyword; exclude drops a
    category whose name contains any exclude keyword. Both are case-insensitive substring matches
    with the same comma-separated keyword semantics as the asset filters, and empty lists are
    no-ops. The input is assumed already sorted by category name, and order is preserved.
    """
    pool = categories
    include = _split_keywords(section_cfg.get("include", ""))
    if include:
        pool = [c for c in pool if any(keyword in str(c.get("name", "")).lower() for keyword in include)]
    exclude = _split_keywords(section_cfg.get("exclude", ""))
    if exclude:
        pool = [c for c in pool if not any(keyword in str(c.get("name", "")).lower() for keyword in exclude)]
    return pool


def _pick_detail_categories(section_cfg: dict, pool: list[dict], rng: random.Random) -> list[dict]:
    """Draw a pick count and select that many distinct categories from a name-sorted pool.

    The count is drawn uniformly in [min, max] (max below min behaves as min) and clamped to the
    pool size, so an empty pool yields no picks. The count draw is always made when the section
    is enabled, even for an empty pool, so one section's pool size never shifts another section's
    draws. Categories are sampled without replacement.
    """
    section_min = int(section_cfg.get("min", 0))
    section_max = int(section_cfg.get("max", 0))
    if section_max < section_min:
        section_max = section_min
    count = rng.randint(section_min, section_max)
    count = min(count, len(pool))
    if count <= 0:
        return []
    return rng.sample(pool, count)


def _draw_detail_value(deviation: float, has_opposites: bool, rng: random.Random) -> tuple[float, str]:
    """Draw one (magnitude, polarity) pair for a detail pick.

    The sign is drawn first (a 50/50 "positive"/"negative" pick, only when the category has an
    opposites table), then the magnitude uniformly in [0.25 * deviation, deviation]. Even a zero
    deviation consumes exactly the same draws, so a section's deviation never shifts the picks.
    """
    polarity = "positive"
    if has_opposites:
        polarity = "positive" if rng.random() < 0.5 else "negative"
    magnitude = rng.uniform(deviation * _DETAIL_MAGNITUDE_FLOOR_FACTOR, deviation)
    return magnitude, polarity


def _detail_targets_for_category(category: dict, deviation: float, symmetry: bool,
                                 rng: random.Random) -> list[dict]:
    """Build the target stack entries for one picked category.

    For a plain (unsided) category one value is drawn and applied to the unsided target. For a
    sided category (has_left_and_right) the "left"/"right" opposite keys are used: with symmetry
    on a single value is mirrored to both sides, with symmetry off the left and right sides get
    independent draws (left first). A zero magnitude yields no entry, but its draws are still made.
    """
    opposites = category.get("opposites") or {}
    has_opposites = bool(opposites)
    has_lr = bool(category.get("has_left_and_right"))

    entries: list[dict] = []
    if has_lr and not symmetry:
        for side in ("left", "right"):
            magnitude, polarity = _draw_detail_value(deviation, has_opposites, rng)
            _append_detail_entry(entries, category, opposites, has_opposites, side, polarity, magnitude)
        return entries

    # One draw, applied to the unsided target or mirrored across both sides of a sided category.
    magnitude, polarity = _draw_detail_value(deviation, has_opposites, rng)
    for side in (("left", "right") if has_lr else ("unsided",)):
        _append_detail_entry(entries, category, opposites, has_opposites, side, polarity, magnitude)
    return entries


def _append_detail_entry(entries: list[dict], category: dict, opposites: dict, has_opposites: bool,
                         side: str, polarity: str, magnitude: float) -> None:
    """Append one {"target", "value"} entry for a category side, skipping zero magnitudes.

    The magnitude is always positive (the sign is expressed by which opposing target is chosen),
    matching how the model panel loads a decr/incr target with a positive weight.
    """
    if magnitude <= 0.0:
        return
    if has_opposites:
        target_name = opposites.get(polarity + "-" + side, "")
    else:
        target_name = _one_sided_target_name(category, side)
    if target_name:
        entries.append({"target": target_name, "value": magnitude})


def _one_sided_target_name(category: dict, side: str) -> str:
    """Resolve the single target name for a category that has no opposites table.

    Such a category is one-sided (0.0 - 1.0 range); its name is used directly, with an "l-"/"r-"
    prefix for the left/right side of a sided category. This is a defensive fallback: the system
    categories in target.json all carry an opposites table.
    """
    name = str(category.get("name", ""))
    if not name:
        targets = category.get("targets") or []
        name = str(targets[0]) if targets else ""
    if not name:
        return ""
    if side == "left":
        return "l-" + name
    if side == "right":
        return "r-" + name
    return name
