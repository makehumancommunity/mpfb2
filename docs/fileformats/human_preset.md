# Human Preset

This file explains the human preset ("save file") JSON format used by MPFB.

## Purpose

A human preset file stores a complete character definition: body shape, rig, body parts, clothes, materials,
and color adjustments. Presets allow saving and restoring fully configured characters. Files are named
`human.<preset_name>.json` and stored in the user config directory.

## Structure

A human preset is a JSON object created by `HumanService.serialize_to_json_file()` in
`src/mpfb/services/humanservice.py`. It combines data from multiple populate methods that each fill
in a section of the preset.

In those cases where a key represents a reference to an asset, the asset path is relative to any of
the specified asset roots (that it, AssetService will look through all asset roots until it finds the asset).
The first segment of the path is the key name, the rest usually a subdirectory plus an asset filename.

Thus something like this:

```
{
   ...
   "eyes": "high-poly/high-poly.mhclo"
   ...
}
```

Will indicate an asset `[any asset root]/eyes/high-poly/high-poly.mhclo`. 

When "asset" is mentioned in the following, it is the above pattern that is indicated.

### Top-level keys

#### Body shape

Two keys control the overall shape of the character: 

- `phenotype` (object) — Macro morph values. Keys are target paths (e.g. `"Macrodetails/Gender"`, `"Macrodetails/Age"`) and values are floats representing slider positions for sliders normally found on the "phenotype" modeling panel.
- `targets` (array of strings) — Names of detail morph targets applied to the character. These correspond to the sliders on all other modeling panels.

#### Rig

- `rig` (string) — Rig type identifier, e.g. `"game_engine"`, `"default"` and so on.

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

- `clothes` (array) — A list of assets

#### Makeup

- `makeup` (array of strings) — File named pointing to Ink layer JSON files.

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

- `color_adjustments` (object) — Per-object color modifications, keyed by object UUID. This will only modify assets with a MHCLO material. Each entry contains three keys:
  - `Color1` and `Color2`. These are RGBA values for the input sockets on the color mix node. Color2 will usually have a diffuse texture connected, so most of the time it is not used.
  - `Fac`: The balance between Color1 and Color2. A Fac of 0.0 will override the diffuse texture completely with Color 1.
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
