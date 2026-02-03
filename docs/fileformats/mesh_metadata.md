# Mesh Metadata

This file explains the mesh metadata files used by MPFB to describe the base mesh structure.

## Purpose

Mesh metadata files provide structural information about the MakeHuman HM08 base mesh: vertex group
definitions, body part dimensions, symmetry mappings, and proxy correction flags. These files are
located in `src/mpfb/data/mesh_metadata/`.

## Files

### hm08_config.json — Mesh configuration

Defines bounding box dimensions, selection groups, and vertex group ranges for the base mesh.

#### Top-level keys

- `description` (string) — Human-readable description, e.g. `"MakeHuman HM08 basemesh"`.
- `dimensions` (object) — Bounding box coordinates for named body regions.
- `select_groups` (object) — Named selection sets that map to one or more vertex groups.
- `groups_by_range` (object) — Vertex index ranges for each vertex group.

#### Dimensions

Each key in `dimensions` is a body region name (e.g. `"Body"`, `"Head"`, `"Teeth"`, `"Eye"`). The value is
an object with integer fields: `xmin`, `xmax`, `ymin`, `ymax`, `zmin`, `zmax`.

#### Select groups

Each key is a selection group name (e.g. `"BODY"`, `"SKIRT"`, `"EYES"`). The value is an array of vertex group
names that belong to this selection set.

Selection group is not used in MPFB, but it is kept for compatibility with MakeHuman.

#### Groups by range

Each key is a vertex group name (e.g. `"body"`, `"helper-skirt"`). The value is a two-element array
`[start_vertex_index, end_vertex_index]` defining the inclusive vertex index range for that group.

### basemesh_vertex_groups.json — Vertex group definitions

Maps vertex group names to their vertex index ranges. Each key is a group name and each value is an array
of `[start, end]` pairs (inclusive ranges). A group can have multiple non-contiguous ranges.

These are extra groups defined on top of those specified by hm08_config.json.

#### Group types

- **Body groups** — `"body"` and general mesh regions.
- **Helper groups** — Prefixed with `"helper-"` (e.g. `"helper-l-eye"`, `"helper-hair"`). Non-deforming geometry for eyes, teeth, eyelashes, etc.
- **Joint groups** — Prefixed with `"joint-"` (e.g. `"joint-head"`, `"joint-l-ankle"`). Define bone deformation regions.
- **Symmetry groups** — `"Left"`, `"Mid"`, `"Right"` for symmetry and mirroring operations.

#### Example

```json
{
    "body": [[0, 13379]],
    "helper-skirt": [[18002, 18721]],
    "HelperGeometry": [[13380, 13605], [14598, 19149]],
    "joint-head": [[13636, 13643]],
    "Left": [[6784, 6892], [6896, 6897]]
}
```

### hm08.mirror — Vertex mirror mapping

A plain text file (not JSON) mapping left-side vertices to their right-side counterparts. Each line has the format:

```
LEFT_INDEX MIRROR_INDEX r
```

- `LEFT_INDEX` (integer) — Vertex index on one side.
- `MIRROR_INDEX` (integer) — Corresponding vertex index on the other side.
- `r` — Side indicator.

Used for mesh mirroring and symmetry operations.

### proxy_corrective.json — Proxy correction flags

Maps proxy mesh UUIDs to correction settings.

```json
{
    "uuid-string": {
        "fix_leftright_weights_for_groups": true
    }
}
```

- Each key is a proxy UUID (string).
- `fix_leftright_weights_for_groups` (boolean) — Whether to automatically fix weight issues between left/right vertex group pairs for this proxy.

This is a remainder of an experiment which was not really finished. It is mostly unused.

### Compressed lookup tables

The `mesh_metadata/` directory also contains `.json.gz` files with face and vertex topology lookup tables,
and a `uv_layers/` subdirectory with compressed UV coordinate data. These are large machine-generated files
used internally by the mesh processing code.
