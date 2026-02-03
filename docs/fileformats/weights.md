# Vertex Weights

This file explains the vertex weights JSON format used by MPFB.

## Purpose

A vertex weights file assigns deformation weights from bones (or special groups) to individual mesh vertices.
These files are used to skin the MakeHuman base mesh to an armature. Weights files are located alongside
rig files in `src/mpfb/data/rigs/standard/` and `src/mpfb/data/rigs/rigify/`, named `weights.<rig_type>.json`.

## Structure

A weights file is a JSON object with metadata fields and a `weights` object containing all bone-to-vertex
assignments. Files are loaded by `RigService.load_weights()` and written by `RigService.get_weights()`
in `src/mpfb/services/rigservice.py`.

### Metadata

- `copyright` (string) — Copyright notice.
- `description` (string) — Human-readable description, typically `"Weights for a rig"`.
- `license` (string) — License identifier, typically `"CC0"`.
- `name` (string) — Display name, typically `"MakeHuman weights"`.
- `version` (integer) — Format version. Currently `110`.

### Weights object

The `weights` key maps to an object where:

- Each **key** is a bone or vertex group name (string).
- Each **value** is an array of `[vertex_index, weight]` pairs.

Each pair is a two-element array:

- Element 0 (integer) — Zero-based vertex index into the mesh.
- Element 1 (float) — Weight value in the range 0.0 to 1.0. Stored with full floating-point precision. Values below 0.0001 are excluded during export.

A single vertex can appear in multiple bone arrays. When applying weights, entries use `ADD` mode so overlapping assignments combine.

### Group types

**Regular bone groups** correspond to deformable bones in the armature (e.g. `"breast.L"`, `"finger1-2.R"`).

**Mask groups** are prefixed with `"mhmask-"` (e.g. `"mhmask-preserve-volume"`, `"mhmask-no-smooth"`). These control Blender modifier behavior rather than bone deformation.

**Rigify deform bones** are prefixed with `"DEF-"` (e.g. `"DEF-forearm.L.001"`). The loader automatically maps between `DEF-` prefixed and unprefixed names as needed.

### Naming conventions by rig type

| Rig type | Left/right convention | Example |
|----------|----------------------|---------|
| default | `.L` / `.R` | `breast.L` |
| game_engine | `_l` / `_r` | `breast_l` |
| rigify | `DEF-` prefix with `.L` / `.R` | `DEF-upper_arm.L` |
| mixamo | `mixamorig:` prefix | `mixamorig:LeftArm` |

## Example content

```json
{
    "copyright": "(c) the guy who clicked the save weights button",
    "description": "Weights for a rig",
    "license": "CC0",
    "name": "MakeHuman weights",
    "version": 110,
    "weights": {
        "breast.L": [
            [1399, 0.01600159890949726],
            [1400, 0.01799819990992546],
            [1401, 0.022297769784927368]
        ],
        "breast.R": [
            [1528, 0.012602520175278187],
            [1890, 0.04399560019373894]
        ],
        "spine01": [
            [800, 0.85],
            [801, 0.92],
            [802, 0.76]
        ]
    }
}
```
