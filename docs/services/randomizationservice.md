# RandomizationService

## Overview

RandomizationService concentrates the core logic for the "random human" feature. It produces a human with a randomized phenotype from a randomization spec, and
is intended to later be extended with detail, asset and batch randomization.

The core functions in this service are deliberately *pure*: they do not touch any `bpy` objects and they never use the global `random` module state. Instead a
caller-supplied `random.Random` instance is threaded through every draw. This keeps sampling reproducible (the same seed and the same spec always produce the
same result) and cheap enough to be called in a loop when batch randomization is added later.

The canonical phenotype representation is the "macro info dict" produced by `TargetService` (see [targetservice.md](targetservice.md)), for example:

```python
{ "gender": 0.5, "age": 0.5, "muscle": 0.5, "weight": 0.5, "proportions": 0.5,
  "height": 0.5, "cupsize": 0.5, "firmness": 0.5,
  "race": {"asian": 0.33, "caucasian": 0.33, "african": 0.33} }
```

A "randomization spec" is a plain nested dict which is also what gets saved as a preset. It has a top-level `version` field and named sections, so later
sub-features can add sibling sections without breaking older presets:

```python
{
  "version": 4,
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
  },
  "creation": {                    # duplicated creation settings, written by the UI layer
    "scale_factor": "METER",
    "detailed_helpers": True, "extra_vertex_groups": True, "mask_helpers": True,
    "rig": "default",              # NONE | a built-in rig | rigify.* | custom.<name>
    "auto_generate_rigify": True,  # generate the full rig from a rigify metarig
    "meta_rig_action": "hide"      # keep | hide | delete the metarig after generation
  },
  "assets": {
    "asset_material_type": "MAKESKIN",  # GAMEENGINE | MAKESKIN, applied to all bodyparts but eyes
    "skin": {
      "enabled": True,             # apply a randomly picked skin material
      "match_gender": True,        # keep only skins whose name matches the gender label
      "match_age": True,           # ...the age label
      "match_race": True,          # ...the dominant race label
      "fallback": True,            # relax phenotype filters (age, then race, then gender) if empty
      "pack": "",                  # keep only skins in a pack whose name contains this
      "include": "",               # keep skins whose name contains any of these keywords
      "exclude": "special_suit",   # drop skins whose name contains any of these keywords
      "skin_type": "MAKESKIN",     # GAMEENGINE | MAKESKIN | ENHANCED | ENHANCED_SSS | LAYERED
      "material_instances": True
    },
    "eyes": {                      # eyes are a drop-down, not a randomized pool
      "mode": "LOWPOLY",           # DONOTADD | HIGHPOLY | LOWPOLY
      "material_type": "MAKESKIN", # GAMEENGINE | MAKESKIN | PROCEDURAL_EYES
      "randomize_alt_materials": True   # pick a random iris colour
    },
    "hair": {
      "enabled": True,             # attach a randomly picked hair
      "match_gender": False,       # keep only hair whose name matches the gender label
      "fallback": True,            # drop only the gender filter if nothing matches
      "pack": "", "include": "", "exclude": "",
      "randomize_alt_materials": False  # pick a random hair colour
    },
    "eyebrows": {"enabled": True, "pack": "", "include": "", "exclude": ""},
    "eyelashes": {"enabled": True, "pack": "", "include": "", "exclude": ""},
    "teeth": {"enabled": True, "pack": "", "include": "", "exclude": ""},
    "tongue": {"enabled": True, "pack": "", "include": "", "exclude": ""},
    "clothes": {                     # one subsection per body slot; at most one garment per slot
      # slots: head, full_body, upper_body, lower_body, hands, feet, underwear, accessories
      "full_body": {
        "enabled": True,             # this slot may produce a garment
        "chance": 25,                # percent chance, per character, that it does
        "pack": "",                  # keep only garments in a pack whose name contains this
        "include_any": "suit,uniform,overall,jumpsuit,robe,armor,armour,kimono,tunic",
        "include_female": "dress,gown",   # unioned with include_any for female characters
        "include_male": "",               # unioned with include_any for male characters
        "exclude": ""                # drop garments whose name contains any of these
      }
      # ...the other seven slots have the same shape...
    }
  }
}
```

The spec format version is currently **4**. A preset written before a section existed is
preserved untouched on load and that concern is then treated as **disabled**: a version-1
preset (no `assets`) loads with skin and every bodypart disabled; a version-2 preset (skin
only) loads with every bodypart disabled and no eyes; a version-3 preset (no `assets.clothes`)
loads with clothes randomization disabled; a preset without a `creation.rig` key loads with the
rig set to **No rig**. So an older preset keeps producing exactly the character it did before.
A **missing bodypart subsection means that type is disabled** (for eyes, not added); likewise a
**missing `assets.clothes` section, or a missing slot subsection, means that slot is disabled**.
The shared `assets.asset_material_type` applies to every attached bodypart and garment except
the eyes, which carry their own `material_type`.

The attributes that have a discrete mode (`gender`, `age` and `race`) carry an `allowed` list of the value names eligible to be picked in that mode. A missing
`allowed` list (as in presets written before this field existed) means every value is allowed. An empty `allowed` list means the attribute is treated as
excluded — see the discrete sampling rules below.

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

Get the built-in randomization spec. All attributes are included, each with the built-in neutral (0.5), a moderate default deviation (0.15) and a bell
distribution, and all toggles off. The returned spec also carries the default `assets` sections: the `skin` section (skin randomization on, all three phenotype
filters and the fallback on, an `exclude` of `special_suit`), the shared `asset_material_type`, and one section per bodypart type (all randomized types on, hair
gender filter off, eyes low-poly with randomized iris).

**Returns:** `dict` — A fresh randomization spec dict.

---

#### get_default_skin_asset_spec()

Get a fresh copy of the default `assets.skin` section (the same dict nested inside `get_default_phenotype_spec()`). Used by the UI to reset the skin controls to
their defaults.

**Returns:** `dict` — A fresh skin asset spec dict.

---

#### get_bodypart_types()

Get the bodypart types in the fixed order they are drawn in: `["eyebrows", "eyelashes", "eyes", "hair", "teeth", "tongue"]` (alphabetical, matching the asset
subdir names). This order is the single source of truth for the UI and the operator, so a seed reproduces the same picks. `"eyes"` is included even though it is
picked from a drop-down rather than a pool.

**Returns:** `list` — The ordered bodypart type names.

---

#### get_plain_bodypart_types()

Get the plain randomized bodypart types (those with only pack / include / exclude filters): `["eyebrows", "eyelashes", "teeth", "tongue"]` — i.e. every bodypart
type except the special `"eyes"` and `"hair"`.

**Returns:** `list` — The ordered plain bodypart type names.

---

#### get_default_bodypart_asset_spec(bodypart)

Get a fresh copy of the default `assets.<bodypart>` section. Used by the UI to reset a bodypart's controls to their defaults.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bodypart` | `str` | — | One of the values returned by `get_bodypart_types()`. Any other value raises `ValueError`. |

**Returns:** `dict` — A fresh bodypart asset spec dict (the shape depends on whether the type is `eyes`, `hair` or a plain type).

---

#### get_clothes_slots()

Get the clothes slot names in body order: `["head", "full_body", "upper_body", "lower_body", "hands", "feet", "underwear", "accessories"]`. This is the
canonical slot list used by the UI (which supplies only the display labels). Note the rng draw order is different (full body first, then alphabetical) and is
internal to `pick_random_clothes`, so the UI order does not affect reproducibility.

**Returns:** `list` — The ordered clothes slot names.

---

#### get_default_clothes_asset_spec(slot)

Get a fresh copy of the default `assets.clothes.<slot>` section. Used by the UI to reset a slot's controls to their defaults.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `slot` | `str` | — | One of the values returned by `get_clothes_slots()`. Any other value raises `ValueError`. |

**Returns:** `dict` — A fresh clothes slot spec dict (`enabled`, `chance`, `pack`, `include_any`, `include_female`, `include_male`, `exclude`).

---

#### get_discrete_value_names(attribute)

Get the canonical value names for an attribute which has a discrete mode. These are the keys used in an attribute's `allowed` list, returned in definition
order. This is the authoritative source for the value names, so callers (such as the UI) do not have to duplicate them.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `attribute` | `str` | — | One of `"gender"`, `"age"` or `"race"`. Any other value raises `ValueError`. |

**Returns:** `list` — The ordered value names (`["female", "male"]`, `["baby", "child", "young", "old"]` or `["asian", "caucasian", "african"]`).

---

### Sampling

#### sample_value(distribution, neutral, max_deviation, rng)

Draw a single clamped value for one attribute. The value is drawn from the requested probability distribution centered on the neutral value, then clamped first
to the deviation range and then to the full range (0.0–1.0). All clamping happens here so call sites do not have to repeat it.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `distribution` | `str` | — | One of `"flat"`, `"bell"`, `"pyramid"` or `"peak"`. Unknown values fall back to `"bell"`. |
| `neutral` | `float` | — | The value the distribution is centered on. |
| `max_deviation` | `float` | — | The one-sided maximum distance from the neutral value. |
| `rng` | `random.Random` | — | The random generator instance to draw from. |

**Returns:** `float` — A value in the range 0.0–1.0.

---

#### randomize_macro_info_dict(spec, rng)

Produce a randomized macro info dict from a randomization spec. This is a pure function: it does not touch any `bpy` objects and only draws from the supplied
generator. The result has the same shape as `TargetService.get_default_macro_info_dict()` and can be passed straight to
`HumanService.create_human(macro_detail_dict=...)`.

Gender is discrete (woman/man) unless `discrete_gender` is unset; age is continuous unless `discrete_age` snaps it to one of the four anchors (baby, child,
young, old); race weights are randomized independently and normalized unless `discrete_race` picks exactly one. Cupsize and firmness are only randomized when
the randomized gender falls on the female side and the randomized age is at or above the young-adult threshold; otherwise they are forced to their neutral
value.

In each discrete mode a value is picked **uniformly among the attribute's `allowed` values** (there is no neutral-based bias). When an attribute's `allowed`
list is empty, the attribute is treated as excluded: `gender` and `age` fall back to their `neutral` value, and `race` falls back to an even mix of all three
weights.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `spec` | `dict` | — | A randomization spec, as produced by `get_default_phenotype_spec()`. |
| `rng` | `random.Random` | — | The random generator instance to draw from. |

**Returns:** `dict` — A macro info dict with randomized values.

---

### Description

#### describe_macro_info_dict(macro, seed)

Produce a one-line human-readable summary of a generated character, used for the "create random human" operator's info report. Display labels are resolved from
the generated values: the age label is the closest age anchor (baby, child, young, old), the gender label is `female` below 0.4 / `male` above 0.6 / `neutral`
in between (a display-only band that does not affect any randomization logic), and the race label is the race whose weight is above 0.5, or `mixed race` if none
is. The race weights are listed in african/asian/caucasian order and values are rounded to two decimals.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `macro` | `dict` | — | A macro info dict, as produced by `randomize_macro_info_dict()`. |
| `seed` | `int` | — | The seed the character was generated with. |

**Returns:** `str` — For example `"Generated with seed 123: A young (0.6) caucasian (0.0/0.0/1.0) female (0.1)"`.

---

### Skin randomization

These functions are pure and drive the "Skin" sub-panel. The phenotype label helpers translate a macro info dict into the labels a skin name is matched against;
`pick_random_skin` applies the filters and draws a skin. The candidate list is passed in by the caller (the operator discovers the installed skins), so the
service never touches `AssetService` and stays unit-testable without installed assets.

#### skin_gender_label(macro)

Get the gender label used when matching a skin against the randomized gender: `"female"` below 0.5, `"male"` at or above. This is a binary split, deliberately
unlike the three-band display labels used by `describe_macro_info_dict`.

**Returns:** `str` — `"female"` or `"male"`.

---

#### skin_age_label(macro)

Get the age label used when matching a skin against the randomized age, one of five bands: `baby`, `child`, `young`, `middleage`, `old`. Unlike the four age
anchors that drive sampling, this includes a dedicated `middleage` band (roughly 0.65–0.85) because the system skins use `middleage` in their names.

**Returns:** `str` — One of `"baby"`, `"child"`, `"young"`, `"middleage"` or `"old"`.

---

#### skin_race_label(macro)

Get the race label used when matching a skin against the randomized race: the race whose weight is above 0.5, or `None` for a mixed-race character (in which
case the race filter is skipped).

**Returns:** `str | None` — `"asian"`, `"caucasian"`, `"african"` or `None`.

---

#### pick_random_skin(spec, macro, candidates, rng)

Pick one skin from a list of candidate dicts according to the spec's `assets.skin` section. Returns `None` when skin randomization is disabled, there are no
candidates, or nothing matches (even after fallback).

The candidate list is **sorted by name before drawing**, so the pick depends only on the seed, the spec and the set of candidates — never on the order the
caller discovered them in (filesystem enumeration order is not deterministic).

The **pack**, **include** and **exclude** filters express hard user intent and are always applied. The **include**/**exclude** filters take comma-separated
keyword lists (whitespace trimmed, empty entries ignored; a single keyword behaves as a plain substring): include keeps a skin whose name contains *any*
keyword, exclude drops a skin whose name contains *any* keyword. The three **phenotype** filters (gender, age, race) narrow the pool further; when the pool is
empty and `fallback` is on, they are dropped one at a time in the order **age, then race, then gender**, until the pool is non-empty.

All name matching is case-insensitive. Two labels are substrings of a longer label (`male` inside `female`, `asian` inside `caucasian`); the longer label is
stripped from the name before the shorter one is tested, so `male` does not match inside `young_caucasian_female2` and `asian` does not match inside a
`caucasian` name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `spec` | `dict` | — | A randomization spec; its `assets.skin` section is read. |
| `macro` | `dict` | — | The randomized macro info dict, used to resolve the phenotype labels. |
| `candidates` | `list` | — | Candidate dicts with `name`, `path` and `pack` (or `None`) keys. |
| `rng` | `random.Random` | — | The random generator instance to draw from. |

**Returns:** `dict | None` — The chosen candidate, or `None`.

---

### Bodypart randomization

These functions are pure and drive the "Body parts" sub-panel. They reuse the same filter-and-pick core as `pick_random_skin` (pack / include / exclude filters,
an optional name-label filter, fallback relaxation and sort-before-pick), and the same candidate-list-passed-in contract, so they stay unit-testable without
installed assets.

#### pick_random_bodypart(spec_section, macro, candidates, rng)

Pick one bodypart asset from a list of candidate dicts according to one `assets.<bodypart>` section (hair or a plain type). Returns `None` when the type is
disabled, there are no candidates, or nothing matches (even after fallback).

The **pack**, **include** and **exclude** filters behave exactly as in `pick_random_skin` and are always applied. Only **hair** carries a phenotype filter: when
its `match_gender` toggle is on the pool is narrowed to hair whose name contains the character's gender label (with the same `male`-inside-`female` handling as
skin), and when the gender-filtered pool is empty and `fallback` is on **only the gender filter is dropped** and the pick retried — pack, include and exclude
are never relaxed. The other bodypart types have no phenotype filter. Candidates are sorted by name before drawing.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `spec_section` | `dict` | — | One `assets.<bodypart>` section (hair or a plain type). |
| `macro` | `dict` | — | The randomized macro info dict, used to resolve the hair gender label. |
| `candidates` | `list` | — | Candidate dicts with `name`, `path` and `pack` (or `None`) keys. |
| `rng` | `random.Random` | — | The random generator instance to draw from. |

**Returns:** `dict | None` — The chosen candidate, or `None`.

---

#### pick_random_alternative_material(default_name, alternatives, rng)

Pick one material name uniformly from a default plus its alternatives, used for the eyes / hair alternative-material (iris / hair colour) randomization. The
default and the alternatives are combined, **de-duplicated** (the eyes discovery can yield duplicates) and sorted by name before drawing, so the pick depends
only on the seed and the set of names. When there are no distinct alternatives the default is returned **without drawing** from `rng`, so an asset with no
alternatives does not shift the seed for later draws.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `default_name` | `str` | — | The asset's default material name. |
| `alternatives` | `list` | — | The alternative material names (may contain duplicates or the default). |
| `rng` | `random.Random` | — | The random generator instance to draw from. |

**Returns:** `str` — The chosen material name (the default when there are no alternatives).

---

### Clothes randomization

This function is pure and drives the "Clothes" sub-panel. Unlike skin and bodyparts (one pick per call), it drives all eight clothes slots in a single call so
it can enforce the full-body exclusivity and the strict draw accounting. It reuses the same filtering core (`pack` / `include` / `exclude`, sort-before-pick)
and the same candidate-list-passed-in contract, so it stays unit-testable without installed assets.

#### pick_random_clothes(clothes_section, macro, candidates, rng)

Pick at most one garment per enabled slot from a list of candidate dicts, according to the `assets.clothes` section. Returns a list with one entry per
**enabled** slot, in the fixed draw order, each a dict with keys `slot`, `pick` (the chosen candidate or `None`) and `warning`. Disabled (or missing) slots
produce no entry.

**Slots and draw order.** The eight slots are drawn in a fixed order — **full body first** (so its outcome can gate the upper and lower body slots), then the
rest alphabetically (`accessories`, `feet`, `hands`, `head`, `lower_body`, `underwear`, `upper_body`). This order is the single source of truth for
reproducibility and is independent of the UI's body-order layout.

**Draw accounting.** Each **enabled** slot consumes exactly **one chance draw and one pick draw**, in that order, regardless of whether it fires, is suppressed
or has an empty pool; disabled slots consume none. So changing one slot's chance or filters never shifts another slot's result for a given seed. (This is
stricter than the bodypart rule, which draws only when it actually picks — bodyparts have no cross-slot interactions.)

**Chance.** A slot fires when a per-character draw falls below its `chance` (a 0–100 percent value); at `100` it always fires, at `0` never.

**Pool.** For each slot the pool is the candidates whose name matches `include_any` **or** the gendered list applicable to the character's gender
(`include_female` below gender 0.5, `include_male` at or above — the same binary split as skin), **minus** the `exclude` matches, intersected with the `pack`
filter. The include lists are unioned, not intersected. Matching is case-insensitive name-substring matching with the same comma-separated keyword semantics as
skin. **Empty include lists never select all clothes:** when both applicable include lists are empty, the pool is the pack's clothes if a `pack` term is set, or
**empty** (the slot is skipped) if not.

**Full-body exclusivity.** When the full body slot fires and attaches a garment, the upper body and lower body slots attach nothing for that character. When the
full body flip misses, upper and lower run per their own settings. Other slots are never suppressed. If the full body flip fires but its pool is empty, the
`warning` for the full body entry is `"full_body_empty_fallback"` and the character falls back to separates (upper and lower run normally).

**Cross-slot dedup.** An asset picked for an earlier slot is removed from later slots' pools, so a garment whose name matches several slots is never attached
twice to the same character.

**Warnings.** The `warning` value is `None` for a successful pick, a missed chance or a suppressed slot; `"empty_pool"` when a non-full-body slot fires with an
empty pool; and `"full_body_empty_fallback"` as above. The service reports nothing itself — the operator turns these codes into user-facing WARNINGs.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `clothes_section` | `dict` | — | The `assets.clothes` section (slot name → slot section). |
| `macro` | `dict` | — | The randomized macro info dict, used to resolve the gender label. |
| `candidates` | `list` | — | Candidate dicts with `name`, `path` and `pack` (or `None`) keys. |
| `rng` | `random.Random` | — | The random generator instance to draw from. |

**Returns:** `list` — One dict per enabled slot (`slot`, `pick`, `warning`), in draw order.

---

### Serialization

#### serialize_spec_to_json_string(spec)

Serialize a randomization spec to a JSON string.

**Returns:** `str` — The spec as indented, key-sorted JSON.

---

#### deserialize_spec_from_json_string(json_string)

Deserialize a randomization spec from a JSON string. Unknown sibling sections are preserved untouched, so presets written by later sub-features can still be
read.

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
