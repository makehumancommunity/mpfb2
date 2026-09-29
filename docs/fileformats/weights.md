# Vertex Weights

This file explains the vertex weights JSON format used by MPFB.

## Purpose

A vertex weights file assigns deformation weights from bones (or special groups) to individual mesh vertices.
These files are used to skin the MakeHuman base mesh to an armature. Weights files are located alongside
rig files in `src/mpfb/data/rigs/standard/` and `src/mpfb/data/rigs/rigify/`, named `weights.<rig_type>.json`.

The same format is also used, with the extension `.mhw`, for the custom weights of a fitted child mesh such
as a piece of clothing or a proxy. Those files sit beside the asset's own `.mhclo` or `.proxy` file and are
located by convention from its base name rather than by any declaration inside it; see
[mhclo.md](mhclo.md) for the details.

## Structure

A weights file is a JSON object with metadata fields and a `weights` object containing all bone-to-vertex
assignments. Files are loaded by `RigService.load_weights()` and written by `RigService.get_weights()`
in `src/mpfb/services/rigservice.py`.

### Metadata

**(not parsed)** — the loader reads nothing but the `weights` key, so every field in this group is
informational only. They exist so that the file stays compatible with MakeHuman's MHW format. A parser
should carry them through without acting on them, and must not rely on any particular value: the shipped
files mostly carry the strings that MPFB's writer hardcodes, but not all of them do.

- `copyright` (string) — Copyright notice.
- `description` (string) — Human-readable description, typically `"Weights for a rig"`.
- `license` (string) — License identifier, typically `"CC0"`.
- `name` (string) — Display name, typically `"MakeHuman weights"`.
- `version` (integer) — Format version. Always `110` in the shipped files, and never checked on load, so
  it does not select a parsing variant.

### Weights object

The `weights` key maps to an object where:

- Each **key** is a bone or vertex group name (string).
- Each **value** is an array of `[vertex_index, weight]` pairs.

Each pair is a two-element array:

- Element 0 (integer) — Zero-based vertex index into the mesh.
- Element 1 (float) — Weight value in the range 0.0 to 1.0.

The array may be empty, and that is common: an empty array declares the group without assigning anything
to it. An empty group is skipped when weights are applied, so it neither creates nor clears a vertex group.
In the shipped files 24 of the 163 groups in `weights.default.json` are empty.

A single vertex can appear in multiple bone arrays. When applying weights, entries use `ADD` mode so overlapping assignments combine.

On write, weights are rounded to five decimals and clamped to the 0.0 to 1.0 range, and a weight below
0.0001 is dropped, so a written value is either 0.0001 or greater. On read, no rounding or filtering
happens at all. The precision in real files therefore varies: the files inherited from MakeHuman carry
full floating-point precision, while the ones MPFB has written since carry at most five decimals.

### Group types

**Regular bone groups** correspond to deformable bones in the armature (e.g. `"breast.L"`, `"finger1-2.R"`).

**Mask groups** are prefixed with `"mhmask-"` (e.g. `"mhmask-preserve-volume"`, `"mhmask-no-smooth"`). These control Blender modifier behavior rather than bone deformation.

**Rigify deform bones** are prefixed with `"DEF-"` (e.g. `"DEF-forearm.L.001"`). The loader automatically maps between `DEF-` prefixed and unprefixed names as needed.

Which groups get loaded is decided per group name, and a name which is neither of the above is normally
dropped. A group is loaded when it matches a deforming bone in the target armature — directly, with `DEF-`
added or removed, or through a fallback which maps a `toeN-M.L`/`.R` group onto the single common toe bone
of a no-toes rig — or when it matches a bone the rig is known to generate later, or when its name starts
with `mhmask-`. Everything else in the file is ignored, unless the caller explicitly asks for all groups,
which MPFB does only when loading an asset's `.mhw` companion file. Adding an arbitrarily named group to a
weights file therefore has no effect on a normal rig load.

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
        ],
        "mhmask-preserve-volume": []
    }
}
```
