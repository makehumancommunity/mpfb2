# Material Settings Presets

This file explains the material settings preset JSON formats used by MPFB.

This structure is used both in standalone files (as described below) and as keys in human save files.

## Purpose

Material settings presets store shader parameter values for MPFB's procedural materials. There are two types:

- **Enhanced skin settings** — Per-zone skin parameters (body, ears, lips, etc.) for the enhanced skin shader.
- **Eye settings** — Parameters for the procedural eye shader.

User presets are saved in the user config directory with the naming pattern `enhanced_settings.<name>.json` or `eye_settings.<name>.json`.

## Structure: Enhanced skin settings

An enhanced skin settings file is a JSON object where each key is a body zone name. The values are parameter
dictionaries for that zone.

### Zone names

The standard zones are: `body`, `ears`, `fingernails`, `genitals`, `lips`, `nipple`, `toenails`.

### Zone parameters

Each zone object has these keys:

- `Brightness` (float) — Color brightness adjustment.
- `Clearcoat` (float) — Clearcoat intensity for a shiny appearance. Range 0.0 to 1.0.
- `Clearcoat Roughness` (float) — Roughness of the clearcoat layer. Range 0.0 to 1.0.
- `Contrast` (float) — Color contrast adjustment.
- `Pore detail` (float) — Pore detail level. Range approximately 1.0 to 4.0.
- `Pore distortion` (float) — Distortion of the pore pattern. Range approximately 0.0 to 2.0.
- `Pore scale` (float) — Scale of the pore texture. Range approximately 500 to 4000.
- `Pore strength` (float) — Intensity of pore effects. Range 0.0 to 1.0.
- `Roughness` (float) — Surface roughness. Range 0.0 to 1.0.
- `colorMixIn` (array of 4 floats) — RGBA color to mix into the base color.
- `colorMixInStrength` (float) — How strongly the mix-in color is applied. Range 0.0 to 1.0.

### Example

```json
{
    "body": {
        "Brightness": 0.0,
        "Clearcoat": 0.2,
        "Clearcoat Roughness": 0.4,
        "Contrast": 0.0,
        "Pore detail": 2.0,
        "Pore distortion": 0.5,
        "Pore scale": 2000.0,
        "Pore strength": 0.3,
        "Roughness": 0.45,
        "colorMixIn": [0.5, 0.3, 0.2, 1.0],
        "colorMixInStrength": 0.0
    },
    "lips": {
        "Brightness": 0.0,
        "Clearcoat": 0.5,
        "Clearcoat Roughness": 0.2,
        "Contrast": 0.0,
        "Pore detail": 2.0,
        "Pore distortion": 0.5,
        "Pore scale": 2000.0,
        "Pore strength": 0.1,
        "Roughness": 0.3,
        "colorMixIn": [0.6, 0.2, 0.2, 1.0],
        "colorMixInStrength": 0.0
    }
}
```

## Structure: Eye settings

An eye settings file is a flat JSON object (not zone-keyed) with parameters for the procedural eye shader.

### Parameters

- `Clearcoat` (float) — Clearcoat intensity.
- `Clearcoat Roughness` (float) — Clearcoat roughness.
- `EyeWhiteColor` (array of 4 floats) — Sclera RGBA color.
- `InnerLayerRoughness` (float) — Roughness of the inner eye layer.
- `IrisBumpStrength` (float) — Bump map strength for iris detail.
- `IrisClockwiseMult` (float) — Clockwise pattern multiplier for iris texture.
- `IrisFeatureScale` (float) — Scale of iris procedural features.
- `IrisMajorColor` (array of 4 floats) — Primary iris RGBA color.
- `IrisMinorColor` (array of 4 floats) — Secondary iris detail RGBA color.
- `IrisRadialMult` (float) — Radial pattern multiplier for iris texture.
- `IrisSection1End` (float) — Outer radius of iris section 1.
- `IrisSection2End` (float) — Outer radius of iris section 2.
- `IrisSection3End` (float) — Outer radius of iris section 3.
- `IrisSection4Color` (array of 4 floats) — RGBA color for iris section 4.
- `IrisToEyeWhiteRelation` (float) — Size ratio between iris and sclera.
- `OuterLayerAlpha` (float) — Transparency of the outer cornea layer.
- `OuterLayerColor` (array of 4 floats) — RGBA color tint of the cornea.
- `OuterLayerIOR` (float) — Index of refraction for the cornea.
- `OuterLayerRoughness` (float) — Roughness of the cornea surface.
- `OuterLayerTransmission` (float) — Transmission level of the cornea.
- `PupilColor` (array of 4 floats) — RGBA color of the pupil.
- `PupilSize` (float) — Pupil diameter.

### Example

```json
{
    "Clearcoat": 0.8,
    "Clearcoat Roughness": 0.1,
    "EyeWhiteColor": [0.9, 0.9, 0.9, 1.0],
    "IrisMajorColor": [0.2, 0.4, 0.6, 1.0],
    "IrisMinorColor": [0.1, 0.2, 0.3, 1.0],
    "PupilColor": [0.01, 0.01, 0.01, 1.0],
    "PupilSize": 0.3,
    "OuterLayerIOR": 1.376,
    "OuterLayerTransmission": 1.0,
    "OuterLayerAlpha": 0.1
}
```
