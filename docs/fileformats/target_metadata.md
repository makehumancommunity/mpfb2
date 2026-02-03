# Target and Macro Metadata

This file explains the target metadata JSON files used by MPFB to organize morphing targets.

## Purpose

MPFB uses two JSON metadata files to organize and drive the morphing target system:

- `src/mpfb/data/targets/target.json` — Categorizes all individual morph targets by body region, with left/right flags and opposite-direction pairing.
- `src/mpfb/data/targets/macrodetails/macro.json` — Defines macro-level attributes (gender, age, weight, etc.) with interpolation ranges.

These files are metadata only. The actual morph data lives in `.target.gz` files.

## Structure: target.json

This file is a JSON object where each key is a body region section name (e.g. `"arms"`, `"nose"`, `"torso"`).

### Section object

Each section has these keys:

- `label` (string) — Display name for the UI.
- `include_per_default` (boolean) — Whether this section is visible by default in the UI.
- `categories` (array) — List of deformation category objects.
- `unsorted` (array of strings) — Target names that don't fit into any auto-detected category.

### Category object

Each category within a section has:

- `name` (string) — Internal identifier. Often includes an opposite pair suffix like `"-decr-incr"`, `"-down-up"`, `"-in-out"`.
- `label` (string) — Display label for the UI.
- `has_left_and_right` (boolean) — `true` if the category has separate left (`l-`) and right (`r-`) prefixed targets.
- `opposites` (object) — Maps opposing directions to target names:
  - `negative-left` (string) — Left-side negative direction target. Empty string if not applicable.
  - `negative-right` (string) — Right-side negative direction target.
  - `negative-unsided` (string) — Unsided negative direction target.
  - `positive-left` (string) — Left-side positive direction target.
  - `positive-right` (string) — Right-side positive direction target.
  - `positive-unsided` (string) — Unsided positive direction target.
- `targets` (array of strings) — All target file names in this category (without `.target`/`.target.gz` extension).

The `opposites` structure enables slider UIs where moving left applies the negative target and moving right applies the positive target.

### Example section

```json
{
  "arms": {
    "label": "Arms",
    "include_per_default": true,
    "categories": [
      {
        "name": "lowerarm-scale-depth-decr-incr",
        "label": "lowerarm-scale-depth-decr-incr",
        "has_left_and_right": true,
        "opposites": {
          "negative-left": "l-lowerarm-scale-depth-decr",
          "negative-right": "r-lowerarm-scale-depth-decr",
          "negative-unsided": "",
          "positive-left": "l-lowerarm-scale-depth-incr",
          "positive-right": "r-lowerarm-scale-depth-incr",
          "positive-unsided": ""
        },
        "targets": [
          "l-lowerarm-scale-depth-decr",
          "r-lowerarm-scale-depth-incr",
          "r-lowerarm-scale-depth-decr",
          "l-lowerarm-scale-depth-incr"
        ]
      }
    ],
    "unsorted": []
  }
}
```

## Structure: macro.json

This file has two top-level keys: `macrotargets` and `combinations`.

### Macrotargets

The `macrotargets` object maps macro attribute names to their definitions:

- `label` (string) — Display name.
- `parts` (array) — Interpolation segments covering the 0.0 to 1.0 slider range.

Each part defines a blend between two targets:

- `lowest` (float) — Lower bound of this segment (inclusive). Slightly below 0.0 (e.g. `-0.01`) at the start to handle precision.
- `highest` (float) — Upper bound of this segment (inclusive). Slightly above 1.0 (e.g. `1.01`) at the end.
- `low` (string) — Target name applied at the lower end. Empty string if none.
- `high` (string) — Target name applied at the upper end. Empty string if none.

When a slider value falls within a part's range, both targets are blended:
- `low_weight = 1.0 - position_pct`
- `high_weight = position_pct`

where `position_pct = (value - lowest) / (highest - lowest)`.

Macros with multiple parts (e.g. `age`) subdivide the slider into segments: baby-child, child-young, young-old.

### Combinations

The `combinations` object maps combination names to arrays of macro attribute names. These define which
macrotargets are combined to generate compound targets:

```json
"combinations": {
  "racegenderage": ["race", "gender", "age"],
  "genderagemuscleweight": ["gender", "age", "muscle", "weight"],
  "genderagemuscleweightproportions": ["gender", "age", "muscle", "weight", "proportions"],
  "genderagemuscleweightheight": ["gender", "age", "muscle", "weight", "height"],
  "genderagemuscleweightcupsizefirmness": ["gender", "age", "muscle", "weight", "cupsize", "firmness"]
}
```

The target service uses these combinations to find multi-axis macrodetail target files on disk
(named by concatenating the attribute values) and blend them according to the individual macro slider positions.

### Example macrotarget

```json
{
  "macrotargets": {
    "gender": {
      "label": "Gender",
      "parts": [
        {
          "lowest": -0.01,
          "highest": 1.01,
          "low": "female",
          "high": "male"
        }
      ]
    },
    "age": {
      "label": "Age",
      "parts": [
        {
          "lowest": -0.01,
          "highest": 0.1874998,
          "low": "baby",
          "high": "child"
        },
        {
          "lowest": 0.1874999,
          "highest": 0.49998,
          "low": "child",
          "high": "young"
        },
        {
          "lowest": 0.49999,
          "highest": 1.01,
          "low": "young",
          "high": "old"
        }
      ]
    }
  }
}
```
