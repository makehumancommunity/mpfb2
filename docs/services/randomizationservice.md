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
  "version": 7,
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
  },
  "details": {                       # detail (non-macro) shape targets; one entry per section
    "enabled": True,                 # apply randomized detail targets
    "symmetry": True,                # sided categories get one value on both sides vs independent
    "sections": {                    # keyed by target.json section (arms, head, ...) minus measure
      "arms": {
        "min": 0, "max": 3,          # pick count drawn uniformly in [min, max]; min=max=0 disables
        "include": "",               # keep only categories whose name contains any of these keywords
        "exclude": "",               # drop categories whose name contains any of these keywords
        "deviation": 0.5             # max weight a picked category may reach (0.0 - 1.0)
      }
      # ...the other 20 sections have the same shape; breast and genitals default to min=max=0...
    }
  },
  "batch": {                         # settings for generating several characters in one go
    "count": 10,                     # how many characters to generate
    "strategy": "GRID",              # GRID | RANDOM (random within a rectangle)
    "origin_x": 0.0, "origin_y": 0.0,# GRID: X/Y position of the first character (no Z, stays on floor)
    "spacing_x": 1.0,                # GRID: distance between characters along a row
    "row_length": 10,                # GRID: characters per row before a new row starts
    "row_shift_y": 1.0,              # GRID: Y shift per new row
    "x_min": -5.0, "x_max": 5.0,     # RANDOM: the X bounds of the scatter rectangle
    "y_min": -5.0, "y_max": 5.0,     # RANDOM: the Y bounds of the scatter rectangle
    "min_distance": 0.0,             # RANDOM: minimum spacing (0 = allow overlap)
    "random_rotation": True          # give each character a random rotation around Z
  }
}
```

The spec format version is currently **7**. A preset written before a section existed is
preserved untouched on load and that concern is then treated as **disabled**: a version-1
preset (no `assets`) loads with skin and every bodypart disabled; a version-2 preset (skin
only) loads with every bodypart disabled and no eyes; a version-3 preset (no `assets.clothes`)
loads with clothes randomization disabled; a version-5-or-older preset (no `details`) loads with
detail randomization disabled; a preset without a `creation.rig` key loads with the rig set to
**No rig**. So an older preset keeps producing exactly the character it did before.
A **missing bodypart subsection means that type is disabled** (for eyes, not added); likewise a
**missing `assets.clothes` section, or a missing slot subsection, means that slot is disabled**,
and a **missing `details.sections` entry means that detail section is disabled** (min=max=0).
The `batch` section (added in version 7) is the one documented deviation from "missing means
disabled": batch generation only runs when its own operator is invoked, so there is nothing to
gate, and a version-6-or-older preset (no `batch`) instead loads the **batch defaults** (a single
grid of 10 characters).
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

#### get_default_detail_spec(section_names)

Build the default `details` section for the given `target.json` section names. Detail randomization is on with symmetry on. Every section gets min 0 / max 3,
empty include/exclude filters and a 0.5 max deviation, except the canonical disabled sections (`breast`, `genitals`) which get `min=max=0`. The caller supplies
the section names (derived from `target.json`), so the service stays free of any filesystem or `target.json` knowledge, mirroring the candidates-passed-in
pattern used by the asset picks.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `section_names` | `list` | — | The `target.json` section names to configure (minus `measure`). |

**Returns:** `dict` — A fresh `details` section dict (`enabled`, `symmetry`, `sections`).

---

#### get_default_batch_spec()

Get a fresh copy of the default `batch` section (`count`, `strategy`, the grid origin and spacings
and the random-area bounds, `min_distance` and `random_rotation`). Unlike the other sections it carries
no `enabled` key: batch generation only runs when its operator is invoked, so a preset without
the section loads these defaults rather than a disabled state. Used by the UI to reset the batch
controls and by the batch operator as its fallback when a section is missing.

**Returns:** `dict` — A fresh `batch` section dict.

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

### Detail randomization

This function is pure and drives the "Details" sub-panel. Unlike the asset picks (which choose an installed asset) it randomizes the **detail shape targets** — the
same non-macro targets the model panel exposes as sliders, grouped in `target.json` into sections (`arms`, `head`, ...) and, within each section, into *categories*
(one category is one slider, bundling the opposing `-decr`/`-incr` targets via its `opposites` table). The section/category structure is passed in as plain data
(the caller parses `target.json`), so the service touches neither `TargetService` nor the filesystem and stays unit-testable.

#### pick_random_details(spec_details, sections, rng)

Pick random detail targets and return a flat stack of `{"target": name, "value": float}` dicts ready for `TargetService.bulk_load_targets`. Returns an empty list
(and consumes **no** rng draws) when detail randomization is disabled.

For each section a pick count is drawn uniformly in `[min, max]` (max below min behaves as min), clamped to the filtered pool size, and that many distinct
categories are picked from the pool. The pool is the section's categories after the **include**/**exclude** keyword filters (same comma-separated,
case-insensitive substring semantics as the asset filters, matched against the category name), sorted by category name before the pick.

**Value model.** Each pick draws a **magnitude uniformly in `[0.25 × deviation, deviation]`** and a separate **50/50 sign draw** selecting the decr (`negative`)
or incr (`positive`) target from the category's `opposites` table; a category without an opposites table is one-sided and only ever gets a positive value. This
deliberately differs from `sample_value`: the global **distribution setting does not apply to detail values** — a bell draw centred on the neutral 0.0 would leave
most picks invisibly close to zero. A zero magnitude (deviation 0) yields no stack entry, but its draws are still made so one section's deviation never shifts
another section's picks.

**Symmetry.** A sided category (`has_left_and_right`) counts as one pick either way. With `symmetry` on a single value is applied to both the `l-` and `r-`
targets; with `symmetry` off the left and right sides get independent draws (left first).

**Reproducibility.** Sections are iterated in **sorted name order** and the pool is **sorted by category name** before the pick; per pick the draws are sign, then
value (left before right for an asymmetric sided category). A section missing from the spec contributes nothing and consumes no draws. Iterating `target.json`
dict order or an unsorted category list would silently break seed reproducibility.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `spec_details` | `dict` | — | The spec's `details` section (`None` or empty means disabled). |
| `sections` | `dict` | — | Section name → list of category dicts, as parsed from `target.json`. |
| `rng` | `random.Random` | — | The random generator instance to draw from. |

**Returns:** `list` — A flat list of `{"target": name, "value": float}` dicts, empty when disabled.

---

### Batch randomization

These two pure helpers drive the batch operator. They keep the same purity contract as the rest
of the service (no `bpy`, caller-supplied data and rng) so batch layout is unit-testable.

#### derive_character_seeds(base_seed, count)

Derive one per-character seed for each character in a batch. A master `random.Random(base_seed)`
draws one seed per character, in order, so the seed for character *i* depends only on the base
seed and *i* — the same base seed gives character *i* the same seed whether the batch is 5 or 50
characters, and a character built from its own seed reproduces exactly (the single-character
operator run with that seed produces the same human). Placement is drawn from a **separate**
stream (see `compute_batch_placements`), so toggling placement never shifts a character.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `base_seed` | `int` | — | The batch's base seed. |
| `count` | `int` | — | The number of characters in the batch. |

**Returns:** `list` — The per-character seeds, one per character, in character order.

---

#### compute_batch_placements(batch_spec, count, rng)

Compute the scene placement for each character. The draw order per character is fixed: position
first (for the RANDOM strategy, plus any minimum-distance retries), then the rotation. The GRID
strategy computes its positions from the origin / spacing / row length / row shift and consumes
**no** draws for them (the first character sits at `origin_x`, `origin_y`); the rotation is still
drawn when `random_rotation` is on. Only X and Y are placed (characters stay feet-on-ground at
z=0); the rotation is around Z.

For the RANDOM strategy a nonzero `min_distance` triggers bounded rejection sampling: a position
landing closer than the minimum to an already-placed character is redrawn up to a fixed cap (25),
then accepted with the `overlap` flag set so the caller can warn. This keeps an impossible
constraint (a tiny area with a large minimum distance) from looping forever.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `batch_spec` | `dict` | — | The `batch` section (strategy, spacings, area, minimum distance, rotation). |
| `count` | `int` | — | The number of characters to place. |
| `rng` | `random.Random` | — | The placement rng (kept separate from the per-character seeds). |

**Returns:** `list` — One `{"location": (x, y, 0.0), "rotation_z": float, "overlap": bool}` dict per character, in character order.

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
