# Expression

This file explains the expression JSON format used by MPFB.

## Purpose

An expression file stores a named, weighted combination of ARKit face unit shape keys, allowing
characters to be placed into pre-defined facial expressions. System expressions ship with MPFB in
`src/mpfb/data/expressions/` (when present); user-saved expressions live in the user's data
directory under `expressions/`.

The format is closely modelled on MakeHuman's `.mhpose` format, with two important differences:

- **Keys are ARKit face unit names** (`"browDownLeft"`, `"jawOpen"`, etc.), not bone-pose unit
  names.
- **Values are floats in the `[0, 1]` range** representing shape key weights, not bone rotations.

## File extension and encoding

- The file is a UTF-8 encoded JSON document.
- The recommended file extension is `.json`, matching other MPFB asset files.
- The file must be loadable with the standard library `json` module without custom decoders.

## Top-level keys

- `format_version` (integer, required) — Currently `1`. Incremented whenever the on-disk schema
  changes in a backwards-incompatible way.
- `name` (string, required) — Human-readable expression name. Conventionally lowercased and
  dash-separated for filenames (e.g. `"smile"`, `"angry-shout"`).
- `description` (string, optional) — One- or two-sentence description suitable for tooltip
  display. Defaults to empty string when absent.
- `tags` (array of strings, optional) — Free-form tags used by the asset library tag filter.
  Conventionally lowercase. Defaults to an empty array when absent.
- `face_units` (object, required) — Mapping from ARKit face unit name to weight (float, `[0.0,
  1.0]`). Only non-zero entries are included; zero-valued entries are filtered on save. Keys
  must be members of `ARKIT_FACEUNITS` in `src/mpfb/services/faceservice.py`. An expression
  with no non-zero face units is not a valid expression and is rejected by the composer at save
  time.
- `author` (string, optional) — Asset author. Defaults to empty string.
- `copyright` (string, optional) — Copyright statement. Defaults to empty string.
- `license` (string, optional) — Asset license identifier (e.g. `"CC0"`, `"CC-BY-4.0"`).
  Defaults to empty string.
- `homepage` (string, optional) — URL to the asset's homepage / source page. Defaults to empty
  string.

## Backwards compatibility rules

- A reader must accept the case where a key listed as "required" above is missing, treating it
  as the documented default (empty string for textual fields, empty object for `face_units`,
  the lowest known version for `format_version`). A missing key produces at most a warning,
  never an error.
- Unknown top-level keys are ignored to allow forward compatibility.
- Unknown face unit names inside `face_units` produce a warning and are skipped (a face unit
  added to ARKit in a future revision must not break loading).
- Float weights are rounded to four decimals on save for stable diffs across saves.

## Example

```json
{
    "format_version": 1,
    "name": "subtle-smile",
    "description": "A small, closed-mouth smile suitable for portrait shots.",
    "tags": ["happy", "subtle", "portrait"],
    "face_units": {
        "mouthSmileLeft": 0.35,
        "mouthSmileRight": 0.35,
        "cheekSquintLeft": 0.15,
        "cheekSquintRight": 0.15
    },
    "author": "Jane Example",
    "copyright": "Copyright 2026 Jane Example",
    "license": "CC0",
    "homepage": "https://example.com/jane/expressions"
}
```

## Encoding/decoding shape keys

To distinguish expression shape keys on the basemesh from modeling shape keys (which use the
`$md-` prefix) and from visemes, expression shape keys are stored under the `!ex-` prefix in
Blender — e.g. `"!ex-browDownLeft"`.

**The `!ex-` prefix is a Blender-internal detail only.** The JSON `face_units` object always
uses bare ARKit names as keys (e.g. `"browDownLeft": 0.7`). The translation between bare names
and prefixed shape key names is encapsulated in two `TargetService` helpers:

- `TargetService.expression_name_to_shapekey_name(face_unit_name)` — prepends `!ex-`.
- `TargetService.shapekey_name_to_expression_name(shapekey_name)` — strips `!ex-`, or returns
  `None` if the name does not start with the prefix.

## Producer / consumer

Expression files are produced by the `MakeExpression` composer panel under `Create assets`
(`src/mpfb/ui/create_assets/makeexpression/`) and consumed by the "Use expression" UI defined
in [Using expressions](../../features/expression/expressions_use.md). Both go through
`FaceService.save_expression(filename, expression_dict, metadata)` and
`FaceService.load_expression(filename)` exclusively — UI code does not parse or write the JSON
directly.

## See also

- [`docs/services/faceservice.md`](../services/faceservice.md) — service-layer methods that read
  and write this format.
- [`docs/services/targetservice.md`](../services/targetservice.md) — the two `!ex-` prefix
  helpers.
- [`docs/fileformats/pose.md`](pose.md) — the closest in-repo analogue.
