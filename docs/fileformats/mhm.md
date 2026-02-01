# MHM

This file explains the MHM (MakeHuman Model) file format.

## Purpose

An MHM file is a saved human character created in MakeHuman. It stores all the information needed to reconstruct a
character: body shape modifiers, attached body parts (eyes, hair, etc.), clothes, skeleton choice, and skin material.
When loaded in MPFB, the file is parsed and the character is rebuilt from available assets.

## Structure

An MHM file is a plain-text format. Each line is either a directive or ignored. Lines are processed in order.
There are no comment markers defined in the format; unrecognized lines are silently skipped.

The first line is typically a version declaration. The remaining lines each start with a keyword followed by
space-separated values.

### Version

```
version v1.2.0
```

Declares the MHM format version. This line is not actively validated by MPFB's parser but is expected by MakeHuman.

### Name

```
name <character_name>
```

Sets the character name. If no `name` line is present, MPFB derives the name from the filename (without the `.mhm`
extension).

### Camera

```
camera <x> <y> <z> <rx> <ry> <rz>
```

Stores the MakeHuman viewport camera position and rotation. This line is not used by MPFB.

### Modifier Lines

```
modifier <category>/<target_name> <weight>
```

Modifier lines define body shape. Each line starts with the keyword `modifier` followed by a category path, a target
name, and a floating-point weight. There are two kinds of modifiers:

#### Macro modifiers

Macro modifiers control high-level body parameters. The category prefixes (`macrodetails/`, `macrodetails-universal/`,
`macrodetails-height/`, `macrodetails-proportions/`, `breast/`) are stripped during parsing, and the target name is
matched against a set of known macros:

| Target Name | Parsed As | Typical Range |
|---|---|---|
| Gender | phenotype gender | 0.0 (female) - 1.0 (male) |
| Age | phenotype age | 0.0 (young) - 1.0 (old) |
| Muscle | phenotype muscle | 0.0 - 1.0 |
| Weight | phenotype weight | 0.0 - 1.0 |
| Height | phenotype height | 0.0 - 1.0 |
| BodyProportions | phenotype proportions | 0.0 - 1.0 |
| African | phenotype race african | 0.0 - 1.0 |
| Asian | phenotype race asian | 0.0 - 1.0 |
| Caucasian | phenotype race caucasian | 0.0 - 1.0 |
| BreastSize | phenotype cupsize | 0.0 - 1.0 |
| BreastFirmness | phenotype firmness | 0.0 - 1.0 |

#### Detail modifiers

Any modifier line that does not match a known macro is treated as a detail morph target. The category/target path is
translated into a target fragment reference with the weight. Opposing target pairs (e.g., `decr|incr`) are resolved
based on the sign of the weight: negative values select the first term, positive values select the second.

### Body Part Lines

```
<bodypart_type> <asset_name> [<uuid>]
```

Body part lines assign assets to specific body slots. Recognized body part types are:

- `eyes` - Eye mesh
- `eyelashes` - Eyelash mesh
- `eyebrows` - Eyebrow mesh
- `teeth` - Teeth mesh
- `tongue` - Tongue mesh
- `hair` - Hair mesh
- `proxy` - Proxy mesh (alternative body topology)

Each line contains the body part type, the asset name, and an optional UUID. MPFB resolves the asset by searching
available MHCLO files, matching first by both name and UUID, then falling back to UUID-only or name-only matching.

### Clothes Lines

```
clothes <asset_name> [<uuid>]
```

Each `clothes` line adds a clothing item to the character. Multiple clothes lines can appear. The asset name and
optional UUID are matched against available MHCLO files in the clothes asset directories, using the same matching
strategy as body parts (name + UUID first, then UUID-only, then name-only).

Note: Lines starting with `clothesHideFaces` are not clothes lines. They control face-hiding behavior and are
handled separately.

### Skeleton

```
skeleton <skeleton_file>.mhskel
```

Specifies which skeleton rig to use. MPFB maps the skeleton filename to an internal rig name:

| Filename Contains | Rig Name |
|---|---|
| default | default |
| toes | default_no_toes |
| game | game_engine |
| cmu | cmu_mb |

If no skeleton line is present, the `default` rig is used.

### Skin Material

```
skinMaterial [skins/]<material_path>
```

Specifies the skin material MHMAT file. The `skins/` prefix is stripped if present. 

### Other Lines

```
clothesHideFaces <boolean>
subdivide <boolean>
```

These lines store MakeHuman settings. `clothesHideFaces` controls whether clothing hides underlying body faces.
`subdivide` controls subdivision surface application. These are stored in the file but are not directly parsed
into the human info dictionary by MPFB.

## Parsing Order

MPFB processes the MHM file in two passes:

1. **First pass:** All lines are processed for modifiers, body parts, skeleton, skin material, and name.
2. **Second pass:** Only `clothes` lines (excluding `clothesHideFaces`) are processed.

This two-pass approach ensures that body configuration is fully established before clothes are resolved.

## Example Content

```
version v1.2.0
name testchar
camera 15.0 49.0 0.0 0.0 0.0 1.0
modifier head/head-square 0.422000
modifier breast/BreastSize 0.500000
modifier breast/BreastFirmness 0.500000
modifier macrodetails/Gender 1.000000
modifier macrodetails/Age 0.500000
modifier macrodetails/African 0.000000
modifier macrodetails/Asian 0.000000
modifier macrodetails/Caucasian 1.000000
modifier macrodetails-universal/Muscle 0.721000
modifier macrodetails-universal/Weight 0.361000
modifier macrodetails-height/Height 0.500000
modifier macrodetails-proportions/BodyProportions 0.653000
eyes High-poly 361c783e-0e8a-4a6e-a4e0-b3ef6cf7bbfd
eyelashes Eyelashes01 49b6efab-7c46-4a7f-b7a6-49743a39e2a0
skeleton default.mhskel
skinMaterial skins/young_caucasian_female/young_caucasian_female.mhmat
clothes female_casualsuit01 8d0a6e81-4195-47fa-b235-0323e9cc862c
clothes Sneakers02 0c11e4cb-5cb2-4951-ad2f-916e08fa9e27
clothesHideFaces True
subdivide False
```
