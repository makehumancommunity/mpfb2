# Mesh Metadata

This file explains the mesh metadata files used by MPFB to describe the base mesh structure.

## Purpose

Mesh metadata files provide structural information about the MakeHuman HM08 base mesh: vertex group
definitions, body part dimensions, symmetry mappings, and proxy correction flags. These files are
located in `src/mpfb/data/mesh_metadata/`.

Some of this data is present without being acted on, and as elsewhere in these documents such keys are
marked **(parsed but inert)** when MPFB reads them but nothing acts on the value, and **(not parsed)** when
MPFB ignores them entirely. Anything not marked is read and acted upon.

## Files

### hm08_config.json — Mesh configuration

Defines bounding box dimensions, selection groups, and vertex group ranges for the base mesh.

**(parsed but inert)** — the whole file, not just individual keys. It is loaded in exactly one place,
`Mhclo._get_config_file()`, for the sole benefit of `Mhclo.set_scalings()`, whose body iterates
`dimensions` and then does nothing with the match: the assignment it was written to make is commented
out. `set_scalings()` is called on every clothes, proxy and body part load, so the file is read at
runtime, but no value in it reaches anything. It is documented here because it ships with the addon and
because MakeHuman does use it.

#### Top-level keys

- `description` (string) — Human-readable description; the shipped file says `"MakeHuman HM08 basemesh"`.
- `dimensions` (object) — Bounding box coordinates for named body regions.
- `select_groups` (object) — Named selection sets that map to one or more vertex groups.
- `groups_by_range` (object) — Vertex index ranges for each vertex group.

#### Dimensions

Each key in `dimensions` is a body region name (e.g. `"Body"`, `"Head"`, `"Teeth"`, `"Eye"`). The value is
an object with integer fields: `xmin`, `xmax`, `ymin`, `ymax`, `zmin`, `zmax`.

#### Select groups

Each key is a selection group name (e.g. `"BODY"`, `"SKIRT"`, `"EYES"`). The value is an array of vertex group
names that belong to this selection set.

Selection groups are kept for compatibility with MakeHuman. Like the rest of this file they have no effect
in MPFB, which gets its vertex groups from `basemesh_vertex_groups.json` instead.

#### Groups by range

Each key is a vertex group name (e.g. `"body"`, `"helper-skirt"`). The value is a two-element array
`[start_vertex_index, end_vertex_index]` defining the inclusive vertex index range for that group.

### basemesh_vertex_groups.json — Vertex group definitions

Maps vertex group names to their vertex index ranges. Each key is a group name and each value is an array
of `[start, end]` pairs (inclusive ranges). A group can have multiple non-contiguous ranges.

This is the file MPFB actually builds the base mesh vertex groups from; the `groups_by_range` section of
`hm08_config.json` covers some of the same ground but is not read. On load each `[start, end]` pair is
expanded into an explicit index list, and a small set of further groups which are defined in code rather
than in any file is merged in on top.

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
VERTEX_INDEX MIRROR_INDEX SIDE
```

- `VERTEX_INDEX` (integer) — Vertex index on one side.
- `MIRROR_INDEX` (integer) — Corresponding vertex index on the other side.
- `SIDE` — Side indicator: `l` for a left-side vertex, `r` for a right-side one, and `m` for a vertex on
  the mid line, whose mirror is itself.

The file has exactly one line per vertex in the base mesh, in index order, and the three fields are
separated by single spaces. For hm08 that is 19158 lines covering indices 0 to 19157, of which 9402 are
`l`, 9402 are `r` and 354 are `m`.
Only the `l` and `r` lines are used, one building the left-to-right mapping and the other the
right-to-left one; `m` lines are read and discarded, since mirroring a mid-line vertex is a no-op.

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

The lookup is by the proxy's UUID, and a proxy which is not listed gets no corrective treatment, so the
file is consulted on every proxy load but applies to very few assets — the shipped file contains a single
entry. It is the remainder of an experiment which was not really finished, and
`fix_leftright_weights_for_groups` is the only flag ever implemented: it walks the proxy's vertices and
strips weights which assign a vertex on one side of the mesh to a vertex group belonging to the other
side.

### Compressed lookup tables

The `mesh_metadata/` directory also contains `.json.gz` files with face and vertex topology lookup tables,
and a `uv_layers/` subdirectory with compressed UV coordinate data. These are large machine-generated files
used internally by the mesh processing code.
