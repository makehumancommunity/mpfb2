# Human Preset

This file explains the human preset JSON format used by MPFB.

## Purpose

A human preset file stores a complete character definition: body shape, rig, body parts, clothes, materials,
and color adjustments. Presets allow saving and restoring fully configured characters. Files are named
`human.<preset_name>.json` and stored in the user config directory.

## Structure

A human preset is a JSON object created by `HumanService.serialize_to_json_file()` in
`src/mpfb/services/humanservice.py`. It combines data from multiple populate methods that each fill
in a section of the preset.

### Top-level keys

#### Body shape

- `phenotype` (object) — Macro morph values. Keys are target paths (e.g. `"Macrodetails/Gender"`, `"Macrodetails/Age"`) and values are floats representing slider positions.
- `targets` (array of strings) — Names of detail morph targets applied to the character.

#### Rig

- `rig` (string) — Rig type identifier, e.g. `"rigify.human_toes"`, `"game_engine"`, `"default"`.

#### Body parts

Asset source paths for each body part slot. Each is a string (empty if no asset is assigned):

- `eyes` — Eye mesh asset.
- `eyebrows` — Eyebrow asset.
- `eyelashes` — Eyelash asset.
- `tongue` — Tongue asset.
- `teeth` — Teeth asset.
- `hair` — Hair asset.
- `proxy` — Body proxy mesh (replaces the base mesh surface).

#### Clothes

- `clothes` (array of strings) — Asset source paths for equipped clothing items.

#### Makeup

- `makeup` (array of strings) — Ink layer JSON filenames applied to the character.

#### Skin material

- `skin_mhmat` (string) — Path to the MakeHuman material file used for the skin.
- `skin_material_type` (string) — Material shader type: `"NONE"`, `"MAKESKIN"`, `"ENHANCED"`, `"ENHANCED_SSS"`, `"LAYERED"`, or `"GAMEENGINE"`.
- `skin_material_settings` (object) — Shader parameter values. Structure depends on `skin_material_type`:
  - For `"ENHANCED"` / `"ENHANCED_SSS"`: Zone-keyed object (see [Material Settings](material_settings.md)).
  - For `"LAYERED"`: Keyed by shader group name (`"color"`, `"body"`, `"face"`, `"ears"`, etc.) with node socket values.
  - For other types: Empty object or not present.

#### Eye material

- `eyes_material_type` (string) — Eye shader type: `"NONE"`, `"MAKESKIN"`, `"PROCEDURAL_EYES"`, or `"GAMEENGINE"`.
- `eyes_material_settings` (object) — Eye shader parameters (see [Material Settings](material_settings.md) eye settings). Only populated for `"PROCEDURAL_EYES"`.

#### Color adjustments and alternatives

- `color_adjustments` (object) — Per-object color modifications, keyed by object UUID. Each value has:
  - `saturation` (float)
  - `hue_shift` (float)
  - `lightness` (float)
- `alternative_materials` (object) — Maps object UUIDs to alternative material names.

## Example content

```json
{
    "phenotype": {
        "Macrodetails/Gender": 0.5,
        "Macrodetails/Age": 0.5,
        "Macrodetails-proportions/BodyProportions": 0.5,
        "Macrodetails-height/Height": 0.5,
        "Macrodetails/African": 0.333,
        "Macrodetails/Asian": 0.333,
        "Macrodetails/Caucasian": 0.333
    },
    "targets": [
        "nose-width-incr",
        "chin-height-decr"
    ],
    "rig": "rigify.human_toes",
    "eyes": "eyes/default",
    "eyebrows": "eyebrows/default_brows",
    "eyelashes": "eyelashes/default_lashes",
    "tongue": "tongue/default_tongue",
    "teeth": "teeth/default_teeth",
    "hair": "",
    "proxy": "",
    "clothes": [
        "clothes/male_casualsuit01"
    ],
    "makeup": [],
    "skin_mhmat": "skins/young_caucasian_female/young_caucasian_female.mhmat",
    "skin_material_type": "ENHANCED",
    "skin_material_settings": {
        "body": {
            "Brightness": 0.0,
            "Roughness": 0.45,
            "colorMixIn": [0.5, 0.3, 0.2, 1.0],
            "colorMixInStrength": 0.0
        }
    },
    "eyes_material_type": "PROCEDURAL_EYES",
    "eyes_material_settings": {
        "IrisMajorColor": [0.2, 0.4, 0.6, 1.0],
        "PupilSize": 0.3
    },
    "color_adjustments": {},
    "alternative_materials": {}
}
```
