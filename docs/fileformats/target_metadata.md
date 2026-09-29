# Target and Macro Metadata

This file explains the target metadata JSON files used by MPFB to organize morphing targets.

## Purpose

MPFB uses two JSON metadata files to organize and drive the morphing target system:

- `src/mpfb/data/targets/target.json` — Categorizes all individual morph targets by body region, with left/right flags and opposite-direction pairing.
- `src/mpfb/data/targets/macrodetails/macro.json` — Defines macro-level attributes (gender, age, weight, etc.) with interpolation ranges.

These files are metadata only. The actual morph data lives in `.target.gz` files. See
[target.md](target.md) for the format of those.

Both files are shipped with the addon. `target.json` is generated at build time by
`src/build_utilities/import_targets.py` from the contents of the target directories, so it is not
hand-authored and is not intended to be edited in place — a rebuild overwrites it.

### How to read the key descriptions

Some keys exist in these files without having any effect. Since a third-party parser cannot tell the
difference by looking at the file, the keys are marked:

- **(parsed but inert)** — MPFB reads this key but nothing acts on the value.
- **(not parsed)** — MPFB ignores this key entirely when reading the file.

Anything not marked is read and acted upon.

`target.json` is read in exactly one place, `src/mpfb/ui/model/_modelsubpanels.py`, which builds the
modeling panels from it. That module is therefore the authority on which of its keys matter.

## Structure: target.json

This file is a JSON object where each key is a body region section name (e.g. `"arms"`, `"nose"`, `"torso"`).

### Section object

Each section has these keys, of which only `label` and `categories` are read:

- `label` (string) — Display name for the UI, used as the panel heading.
- `categories` (array) — List of deformation category objects.
- `include_per_default` (boolean) — **(not parsed)** Intended to say whether this section is visible by
  default in the UI. Nothing reads it. Every section panel is created closed regardless of its value, and
  all 23 sections of the shipped file set it to `true` in any case. The build-time generator writes it and
  MPFB sets it on the sections it constructs at runtime, but no consumer ever looks at it.
- `unsorted` (array of strings) — **(not parsed)** Optional. Intended for target names that don't fit into
  any auto-detected category. It is present in every section of the shipped `target.json` and empty in all
  of them, and the key does not occur anywhere under `src/mpfb/`. The only thing that has ever written it
  is the build-time generator `src/build_utilities/import_targets.py`, which used it to catch stray
  MakeHuman targets that did not fit the category model. A parser should skip it rather than try to give
  it meaning. The key is kept deliberately, in case asset packs later reuse this format for their own
  target metadata; it is not deprecated and is not slated for removal.

### Category object

Each category within a section has:

- `name` (string) — Internal identifier. Often includes an opposite pair suffix like `"-decr-incr"`, `"-down-up"`, `"-in-out"`.
- `label` (string) — Display label for the UI.
- `has_left_and_right` (boolean) — `true` if the category has separate left (`l-`) and right (`r-`) prefixed targets.
- `opposites` (object) — Optional. Maps opposing directions to target names:
  - `negative-left` (string) — Left-side negative direction target. Empty string if not applicable.
  - `negative-right` (string) — Right-side negative direction target.
  - `negative-unsided` (string) — Unsided negative direction target.
  - `positive-left` (string) — Left-side positive direction target.
  - `positive-right` (string) — Right-side positive direction target.
  - `positive-unsided` (string) — Unsided positive direction target.
- `targets` (array of strings) — All target file names in this category (without `.target`/`.target.gz` extension).

The `opposites` structure enables slider UIs where moving left applies the negative target and moving
right applies the positive target.

`opposites` is optional, and its absence is meaningful rather than an omission: a category without
opposites is one-sided. Such a category has a single target per side and a slider which only goes from
0.0 to 1.0, whereas a category with opposites gets a slider from -1.0 to 1.0. Every read of the key is
guarded by a presence test, so a parser must treat a missing `opposites` as "one-sided" and not as an
error. Eight of the 234 categories in the shipped `target.json` lack it: `chin-triangle` in the `chin`
section, and the seven `head-*` face shape categories (`head-diamond`, `head-invertedtriangular`,
`head-oval`, `head-rectangular`, `head-round`, `head-square`, `head-triangular`) in the `head` section.

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

### Sections which do not come from the file

The structure above describes the on-disk file. In addition to the sections it contains, MPFB constructs
further sections in memory at import time, from custom and user target directories. These do not come
from any file and are not written back to one.

A runtime-constructed category has a different shape from a file-based one:

- It never has `opposites`, so it is always one-sided.
- It never has `unsorted` — the section it belongs to has no `unsorted` key at all.
- It has an extra key `full_path` (string), the absolute path of the target file. File-based categories
  do not have this, and MPFB falls back to looking the target up by name under the section directory
  when it is absent.

A parser reading `target.json` will never encounter `full_path`, and a parser reproducing MPFB's target
list has to replicate the directory scanning described below in order to arrive at the same set of
sliders.

### Custom and user targets

There is no metadata file for a custom target. The only things MPFB can know about one are its path and
its file name, and everything below is derived from those.

**Custom targets.** `.target` and `.target.gz` files are searched for recursively under the `custom` and
`targets/custom` subdirectories of every data root — MPFB's own data directory, MakeHuman's user data
directory, MPFB's user data directory, and the configured second root. Every match, from every root,
lands in a single section labelled `Custom targets`, regardless of which root or subdirectory it was
found in.

**User targets.** `.target` files are searched for recursively under the `targets` directory of MPFB's
user data directory. These are grouped into one section per directory, using the name of the file's
immediate parent directory both as the section name and as the section label. Note two consequences of
using the bare directory name: a subdirectory whose name collides with a section name in `target.json`
(`arms`, `nose`, …) has its targets appended to that existing section, and a target placed directly in
`targets` rather than in a subdirectory ends up in a section named `targets`.

Only uncompressed `.target` files are found by the user targets scan. A `.target.gz` is picked up under
`custom` and `targets/custom` only. This asymmetry is a known defect rather than a deliberate
restriction, so do not rely on it either way.

**Slider label and identifier.** Both are derived from the file name with the extension removed; the
label additionally has underscores replaced by spaces, so `my_target.target` gives a category named
`my_target` and a slider labelled `my target`. Only the `.target` part of a gzipped name is currently
stripped, so `my_target.target.gz` gives `my_target.gz` and a slider labelled `my target.gz`; that is a
known defect and not how the rule is meant to work.

The name is also used to build a Blender property identifier, together with the section name and any side
prefix, and Blender rejects identifiers of 64 characters or more. A target whose name is too long to fit
is skipped with a warning in the log rather than aborting the addon, so an over-long file name results in
a missing slider.

**Slider icon.** A target in a user targets subdirectory can have an icon: a `.png` or `.thumb` file in
the same directory, with the same basename as the target. If both exist the `.thumb` is used. Targets
found under `custom` and `targets/custom` do not get an icon this way.

**Nothing else can be declared.** A custom target is always one-sided, has no opposites, and cannot
declare left/right symmetry — there is no `.modifier` file, no sidecar JSON, and no way to add a category
to `target.json` from an asset pack. Adding a mechanism for this is an open feature request, not an
undocumented capability.

## Structure: macro.json

This file has two top-level keys: `macrotargets` and `combinations`.

### Macrotargets

The `macrotargets` object maps macro attribute names to their definitions:

- `label` (string) — Display name.
- `parts` (array) — Interpolation segments covering the 0.0 to 1.0 slider range.

Both keys are present on every entry of the shipped file, and no entry carries any other key. The eight
entries are `gender`, `age`, `muscle`, `weight`, `proportions`, `height`, `cupsize` and `firmness`; this
set is fixed in code and adding a ninth entry to the file has no effect.

Each part defines a blend between two targets:

- `lowest` (float) — Lower bound of this segment, **exclusive**. Padded slightly below 0.0 (e.g. `-0.01`) at the start.
- `highest` (float) — Upper bound of this segment, **exclusive**. Padded slightly above 1.0 (e.g. `1.01`) at the end.
- `low` (string) — Target name applied at the lower end. Empty string if none.
- `high` (string) — Target name applied at the upper end. Empty string if none.

A part applies when `lowest < value < highest`. Both bounds are exclusive, which is why the shipped file
looks the way it does:

- The first part of every macro starts at `-0.01` and the last one ends at `1.01`, so that the slider
  extremes 0.0 and 1.0 fall strictly inside a part. Without the padding they would fall on a bound and
  match nothing.
- Consecutive parts never share a boundary value, since with both bounds exclusive a shared value would
  belong to neither part. The `age` parts stop at `0.1874998` and resume at `0.1874999` rather than both
  using the same number. Note that the gap avoids an overlap rather than a hole: the two boundary values
  themselves still belong to no part, as described below.

When a slider value falls within a part's range, both targets are blended:
- `low_weight = 1.0 - position_pct`
- `high_weight = position_pct`

where `position_pct = (value - lowest) / (highest - lowest)`. Both weights are rounded to four decimals.
An empty `low` or `high` contributes no component, so a part can apply a single target that fades in over
its range.

Because the bounds are exclusive, a value landing exactly on a bound falls in no part at all and
contributes no components. This is not only an edge case:

- `height` runs from `-0.01` to `0.49` and from `0.51` to `1.01`, so any value in `[0.49, 0.51]` —
  including the slider midpoint 0.5 — produces no height target at all. The gap is how "average height,
  no modification" is expressed.
- `proportions` has the same arrangement with a smaller gap, `0.4999` to `0.5`, and 0.5 exactly produces
  no proportions target.
- For a macro whose parts nearly meet, such as `age`, the dead band is just the two boundary values. Both
  `age` 0.1874998, the upper bound of the first part, and `age` 0.1874999, the lower bound of the second,
  yield no components; 0.1874997 yields two. Since a slider is unlikely to land on either value, this
  seam is a curiosity rather than a problem — unlike the `height` and `proportions` gaps above, which are
  wide enough to be hit deliberately.

The padding also means the extremes never reach a weight of 1.0. At `gender` 0.0 the components are
`female` 0.9902 and `male` 0.0098, not `female` 1.0, since 0.0 is not the start of the part's range but
0.01 into a range of width 1.02.

Macros with multiple parts (e.g. `age`) subdivide the slider into segments: baby-child, child-young, young-old.

### Combinations

The `combinations` object maps combination names to arrays of macro attribute names:

```json
"combinations": {
  "racegenderage": ["race", "gender", "age"],
  "genderagemuscleweight": ["gender", "age", "muscle", "weight"],
  "genderagemuscleweightproportions": ["gender", "age", "muscle", "weight", "proportions"],
  "genderagemuscleweightheight": ["gender", "age", "muscle", "weight", "height"],
  "genderagemuscleweightcupsizefirmness": ["gender", "age", "muscle", "weight", "cupsize", "firmness"]
}
```

**(not parsed)** — MPFB does not read this section at all, and does not use it to decide which multi-axis
macrodetail target files to look for. The word `combinations` occurs exactly once under `src/mpfb/`, in an
unrelated comment about the length of MakeHuman file names. The same five combinations are hardcoded in `TargetService.calculate_target_stack_from_macro_info_dict()`,
one explicit block of nested loops per combination, each with its own directory prefix and its own
exceptions — `race`/`gender`/`age` skips the `universal` gender component, the cupsize/firmness
combination applies only to the female gender component and excludes some combinations outright. None of
that is expressible in the file.

Editing or removing this section therefore changes nothing, and adding an entry to it does not make MPFB
look for a new family of targets. The section is documented here because it is in the shipped file and a
parser will encounter it, not because a parser needs to act on it. Whether the redundancy should be
resolved by deleting the section or by making the combinations genuinely data-driven is an open question
and not settled.

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
