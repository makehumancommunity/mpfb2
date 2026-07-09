# RandomizationService

## Overview

RandomizationService concentrates the core logic for the "random human" feature. It produces a human with a randomized phenotype from a randomization spec, and is intended to later be extended with detail, asset and batch randomization.

The core functions in this service are deliberately *pure*: they do not touch any `bpy` objects and they never use the global `random` module state. Instead a caller-supplied `random.Random` instance is threaded through every draw. This keeps sampling reproducible (the same seed and the same spec always produce the same result) and cheap enough to be called in a loop when batch randomization is added later.

The canonical phenotype representation is the "macro info dict" produced by `TargetService` (see [targetservice.md](targetservice.md)), for example:

```python
{ "gender": 0.5, "age": 0.5, "muscle": 0.5, "weight": 0.5, "proportions": 0.5,
  "height": 0.5, "cupsize": 0.5, "firmness": 0.5,
  "race": {"asian": 0.33, "caucasian": 0.33, "african": 0.33} }
```

A "randomization spec" is a plain nested dict which is also what gets saved as a preset. It has a top-level `version` field and named sections, so later sub-features can add sibling sections without breaking older presets:

```python
{
  "version": 1,
  "phenotype": {
    "distribution": "bell",        # flat | bell | pyramid | peak
    "discrete_race": False,        # pick exactly one race vs normalized weights
    "discrete_gender": True,       # discrete woman/man vs continuous
    "discrete_age": False,         # snap to an age anchor vs continuous
    "attributes": {
      "gender": {"include": True, "neutral": 0.5, "deviation": 0.15, "allowed": ["female", "male"]},
      "age":    {"include": True, "neutral": 0.5, "deviation": 0.15, "allowed": ["baby", "child", "young", "old"]},
      # ...muscle, weight, height, proportions, cupsize, firmness...
      "race":   {"include": True, "allowed": ["asian", "caucasian", "african"]}
    }
  }
}
```

The attributes that have a discrete mode (`gender`, `age` and `race`) carry an `allowed` list of the value names eligible to be picked in that mode. A missing `allowed` list (as in presets written before this field existed) means every value is allowed. An empty `allowed` list means the attribute is treated as excluded — see the discrete sampling rules below.

All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/randomizationservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.randomizationservice")` |
| `TargetService` | Supplies the neutral macro info dict via `TargetService.get_default_macro_info_dict()` |

## Public API

### Spec construction

#### get_default_phenotype_spec()

Get the built-in randomization spec. All attributes are included, each with the built-in neutral (0.5), a moderate default deviation (0.15) and a bell distribution, and all toggles off.

**Returns:** `dict` — A fresh randomization spec dict.

---

#### get_discrete_value_names(attribute)

Get the canonical value names for an attribute which has a discrete mode. These are the keys used in an attribute's `allowed` list, returned in definition order. This is the authoritative source for the value names, so callers (such as the UI) do not have to duplicate them.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `attribute` | `str` | — | One of `"gender"`, `"age"` or `"race"`. Any other value raises `ValueError`. |

**Returns:** `list` — The ordered value names (`["female", "male"]`, `["baby", "child", "young", "old"]` or `["asian", "caucasian", "african"]`).

---

### Sampling

#### sample_value(distribution, neutral, max_deviation, rng)

Draw a single clamped value for one attribute. The value is drawn from the requested probability distribution centered on the neutral value, then clamped first to the deviation range and then to the full range (0.0–1.0). All clamping happens here so call sites do not have to repeat it.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `distribution` | `str` | — | One of `"flat"`, `"bell"`, `"pyramid"` or `"peak"`. Unknown values fall back to `"bell"`. |
| `neutral` | `float` | — | The value the distribution is centered on. |
| `max_deviation` | `float` | — | The one-sided maximum distance from the neutral value. |
| `rng` | `random.Random` | — | The random generator instance to draw from. |

**Returns:** `float` — A value in the range 0.0–1.0.

---

#### randomize_macro_info_dict(spec, rng)

Produce a randomized macro info dict from a randomization spec. This is a pure function: it does not touch any `bpy` objects and only draws from the supplied generator. The result has the same shape as `TargetService.get_default_macro_info_dict()` and can be passed straight to `HumanService.create_human(macro_detail_dict=...)`.

Gender is discrete (woman/man) unless `discrete_gender` is unset; age is continuous unless `discrete_age` snaps it to one of the four anchors (baby, child, young, old); race weights are randomized independently and normalized unless `discrete_race` picks exactly one. Cupsize and firmness are only randomized when the randomized gender falls on the female side and the randomized age is at or above the young-adult threshold; otherwise they are forced to their neutral value.

In each discrete mode a value is picked **uniformly among the attribute's `allowed` values** (there is no neutral-based bias). When an attribute's `allowed` list is empty, the attribute is treated as excluded: `gender` and `age` fall back to their `neutral` value, and `race` falls back to an even mix of all three weights.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `spec` | `dict` | — | A randomization spec, as produced by `get_default_phenotype_spec()`. |
| `rng` | `random.Random` | — | The random generator instance to draw from. |

**Returns:** `dict` — A macro info dict with randomized values.

---

### Description

#### describe_macro_info_dict(macro, seed)

Produce a one-line human-readable summary of a generated character, used for the "create random human" operator's info report. Display labels are resolved from the generated values: the age label is the closest age anchor (baby, child, young, old), the gender label is `female` below 0.4 / `male` above 0.6 / `neutral` in between (a display-only band that does not affect any randomization logic), and the race label is the race whose weight is above 0.5, or `mixed race` if none is. The race weights are listed in african/asian/caucasian order and values are rounded to two decimals.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `macro` | `dict` | — | A macro info dict, as produced by `randomize_macro_info_dict()`. |
| `seed` | `int` | — | The seed the character was generated with. |

**Returns:** `str` — For example `"Generated with seed 123: A young (0.6) caucasian (0.0/0.0/1.0) female (0.1)"`.

---

### Serialization

#### serialize_spec_to_json_string(spec)

Serialize a randomization spec to a JSON string.

**Returns:** `str` — The spec as indented, key-sorted JSON.

---

#### deserialize_spec_from_json_string(json_string)

Deserialize a randomization spec from a JSON string. Unknown sibling sections are preserved untouched, so presets written by later sub-features can still be read.

**Returns:** `dict` — The parsed spec.

---

#### serialize_spec_to_json_file(spec, file_path)

Serialize a randomization spec to a JSON file at `file_path`.

---

#### deserialize_spec_from_json_file(file_path)

Deserialize a randomization spec from the JSON file at `file_path`.

**Returns:** `dict` — The parsed spec.

## Examples

```python
import random
from mpfb.services import RandomizationService, HumanService

spec = RandomizationService.get_default_phenotype_spec()
spec["phenotype"]["attributes"]["height"]["deviation"] = 0.3

rng = random.Random(1234)
macro = RandomizationService.randomize_macro_info_dict(spec, rng)

basemesh = HumanService.create_human(macro_detail_dict=macro)
```
