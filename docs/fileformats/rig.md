# Rig Definition

This file explains the rig definition JSON format used by MPFB.

## Purpose

A rig definition file describes a skeleton (armature) for a MakeHuman base mesh. It defines the bone hierarchy,
how each bone endpoint is positioned relative to the mesh, and optional Rigify metadata. Rig files are located
in `src/mpfb/data/rigs/standard/` and `src/mpfb/data/rigs/rigify/`.

## Structure

A rig definition file is a JSON object. There are two format versions:

- **Version 100** (legacy): The `bones` object is at the top level alongside a `version` key.
- **Version 110** (current): Adds named bone collections (replacing the old 32-bit layer bitmask) and additional metadata keys.

Files are loaded by `Rig.from_json_file_and_basemesh()` in `src/mpfb/entities/rig.py`. Version 100 files are
automatically upgraded to 110 on load.

### Top-level keys

- `bones` (object, required) — Dictionary mapping bone names to bone definitions.
- `version` (integer, required) — Format version. Current is `110`.
- `is_subrig` (boolean, required) — `true` if this rig must be parented to another rig, `false` for standalone rigs.
- `scale_factor` (float, optional) — Scale factor used during rig creation.
- `collections` (array of strings, optional) — Blender bone collection names (v110+).
- `extra_bones` (array of strings, optional) — Names of non-deforming extra bones.
- `rigify_ui` (object, optional) — Rigify UI configuration metadata.

### Bone entry

Each key in the `bones` object is a bone name, and its value has these fields:

- `head` (object, required) — Position strategy for the bone head. See Position Strategies below.
- `tail` (object, required) — Position strategy for the bone tail. See Position Strategies below.
- `roll` (float, required) — Bone roll in radians.
- `parent` (string, required) — Parent bone name. Empty string for root bones.
- `use_connect` (boolean, required) — Whether the bone connects to its parent's tail.
- `use_inherit_rotation` (boolean, required) — Whether the bone inherits parent rotation.
- `use_local_location` (boolean, required) — Whether to use local location.
- `inherit_scale` (string, required) — Scale inheritance mode: `"FULL"`, `"FIX_SHEAR"`, or `"NONE"`.
- `rigify` (object, required) — Rigify configuration. Can be empty `{}` for non-Rigify rigs.
- `collections` (array of strings, optional) — Bone collection memberships (v110+).
- `constraints` (array, optional) — Bone constraints. See Constraints below.
- `rotation_mode` (string, optional) — Rotation mode: `"QUATERNION"`, `"XYZ"`, `"XZY"`, etc.
- `bendy_bone` (object, optional) — Bendy bone settings. See Bendy Bones below.
- `roll_strategy` (string, optional) — Automatic roll alignment: `"ALIGN_Z_WORLD_Z"` or `"ALIGN_X_WORLD_X"`. When set, the `roll` value is cleared to 0.0.

### Position strategies

The `head` and `tail` objects define how bone endpoints are positioned relative to the base mesh.

#### CUBE

Positions the endpoint at the center of a joint cube defined by a vertex group on the base mesh.

- `strategy` — `"CUBE"`
- `cube_name` (string) — Joint cube vertex group name, e.g. `"joint-spine-1"`.
- `default_position` (array of 3 floats) — Fallback `[x, y, z]` position.
- `offset` (array of 3 floats, optional) — Offset from cube center, scaled by the rig's scale factor.

#### VERTEX

Positions the endpoint at a single mesh vertex.

- `strategy` — `"VERTEX"`
- `vertex_index` (integer) — Index into the base mesh vertex array.
- `default_position` (array of 3 floats) — Fallback `[x, y, z]` position.
- `offset` (array of 3 floats, optional) — Offset from vertex, scaled by the rig's scale factor.

#### MEAN

Positions the endpoint at the average of two or more mesh vertices.

- `strategy` — `"MEAN"`
- `vertex_indices` (array of integers) — Vertex indices to average.
- `default_position` (array of 3 floats) — Fallback `[x, y, z]` position.
- `offset` (array of 3 floats, optional) — Offset from computed mean.

#### XYZ

Takes the X, Y, and Z coordinates from three different vertices. Used for Rigify heel markers.

- `strategy` — `"XYZ"`
- `vertex_indices` (array of 3 integers) — `[x_vertex, y_vertex, z_vertex]`.
- `default_position` (array of 3 floats) — Fallback `[x, y, z]` position.
- `offset` (array of 3 floats, optional) — Offset from computed position.

### Rigify configuration

The `rigify` object stores Rigify-specific metadata for a bone:

- `rigify_type` (string, optional) — Generator type, e.g. `"basic.raw_copy"`, `"limbs.super_limb"`, `"face.skin_eye"`.
- `rigify_parameters` (object, optional) — Generator-specific parameters. May contain simple values (strings, numbers, booleans) or collection references (arrays with keys ending in `_coll_refs`).

### Constraints

The optional `constraints` array defines pose bone constraints. Each constraint has at least:

- `type` (string) — Constraint type: `"ARMATURE"`, `"COPY_TRANSFORMS"`, `"TRANSFORM"`, `"STRETCH_TO"`, `"CHILD_OF"`, etc.
- `name` (string) — Constraint name.
- `subtarget` (string, optional) — Target bone name.
- `target` — `true` (current armature), `false` (none), or an object with a `strategy` key for sub-rig parent lookups.
- `influence` (float, optional) — Influence value, 0.0 to 1.0.

For `ARMATURE` type constraints, a `targets` array provides multiple bone targets with `subtarget` and `weight` fields.

### Bendy bones

The optional `bendy_bone` object configures B-spline deformation. Only non-default values are stored:

- `segments` (integer) — Number of B-spline segments. Default: 1.
- `mapping_mode` (string) — `"STRAIGHT"` or `"CURVED"`. Default: `"STRAIGHT"`.
- `custom_handle_start`, `custom_handle_end` (string) — Bone names for custom handles.
- `handle_type_start`, `handle_type_end` (string) — `"AUTO"`, `"ABSOLUTE"`, or `"RELATIVE"`.
- `easein`, `easeout` (float) — Ease values, 0.0 to 1.0. Default: 1.0.

## Example content

```json
{
  "version": 110,
  "is_subrig": false,
  "collections": ["Torso", "Limbs", "Face"],
  "bones": {
    "root": {
      "head": {
        "strategy": "CUBE",
        "cube_name": "joint-ground",
        "default_position": [0.0, 0.006, 0.0]
      },
      "tail": {
        "strategy": "CUBE",
        "cube_name": "joint-spine-1",
        "default_position": [0.0, 0.019, 0.421]
      },
      "roll": 0.0,
      "parent": "",
      "use_connect": false,
      "use_inherit_rotation": true,
      "use_local_location": true,
      "inherit_scale": "FULL",
      "rigify": {},
      "collections": ["Torso"]
    },
    "spine01": {
      "head": {
        "strategy": "CUBE",
        "cube_name": "joint-spine-1",
        "default_position": [0.0, 0.019, 0.421]
      },
      "tail": {
        "strategy": "CUBE",
        "cube_name": "joint-spine-2",
        "default_position": [0.0, 0.008, 0.514]
      },
      "roll": 0.0,
      "parent": "root",
      "use_connect": true,
      "use_inherit_rotation": true,
      "use_local_location": true,
      "inherit_scale": "FULL",
      "rigify": {
        "rigify_type": "basic.super_copy"
      },
      "collections": ["Torso"]
    }
  }
}
```
