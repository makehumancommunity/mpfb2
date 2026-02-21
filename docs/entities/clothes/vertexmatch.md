# VertexMatch

## Overview

`VertexMatch` maps a single **clothes vertex** to a triplet of **basemesh vertices** using a deterministic four-strategy fallback algorithm. The result is stored in `self.mhclo_line`, which contains exactly the data that becomes one vertex-mapping entry in an MHCLO file.

All matching work runs inside `__init__`. Once the object is constructed, the caller reads `self.mhclo_line` and `self.final_strategy`; no further method calls are needed.

### Matching strategies

Strategies are tried in order; the first one that succeeds sets `self.final_strategy` and `self.mhclo_line`.

1. **EXACT** — search for a target vertex within 0.001 Blender units of the focus vertex using a KDTree. When found, the MHCLO line reduces to a single index (`weights=(1, 0, 0)`, `offsets=(0, 0, 0)`).

2. **RIGID_GROUP** — check whether the matching vertex group on the target mesh contains exactly three vertices. If so, treat those three vertices as a rigid triangle and compute barycentric weights and offsets. This handles small accessories such as buttons or buckles that should scale uniformly with a body part.

3. **SIMPLE_FACE** — find the closest face (by its median point) in the target group. If all vertices of that face belong to the same vertex group as the focus vertex, use those vertices for the barycentric calculation.

4. **EXTENDED_FACE** — examine the 20 nearest faces (by median point) within the matching vertex group. Pick the first face whose normal deviates less than 30 degrees from the direction to the focus vertex.

If none of the four strategies succeeds, `__init__` raises `ValueError`.

### Coordinate-system note

The offset vector stored in `mhclo_line["offsets"]` is in MakeHuman's Y-up convention: the raw Blender `(x, y, z)` displacement `D` becomes `(D[0] / scale, D[2] / scale, -D[1] / scale)` in the MHCLO line. The companion `Mhclo.load` method reverses this swap when reading.

## Source

`src/mpfb/entities/clothes/vertexmatch.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `mathutils.Vector` | Vector arithmetic in barycentric weight calculation |
| `mathutils.geometry` | `normal()` for computing the triangle normal |
| `MeshService` | `closest_vertices()` KDTree query used in the EXACT strategy |
| `LogService` | Logging via `LogService.get_logger("entities.vertexmatch")` |

## Attributes

The following attributes are the primary outputs of the constructor. The input parameters (`focus_obj`, `focus_vert_index`, etc.) are also stored as instance attributes but are not intended for external use.

| Attribute | Type | Description |
|-----------|------|-------------|
| `final_strategy` | str | Which strategy succeeded: `"EXACT"`, `"RIGID_GROUP"`, `"SIMPLE_FACE"`, or `"EXTENDED_FACE"` |
| `mhclo_line` | dict | Mapping result with keys: `"verts"` (list of 3 int), `"weights"` (list of 3 float), `"offsets"` (list of 3 float in MakeHuman coordinates) |

## Public API

### `__init__(focus_obj, focus_vert_index, focus_crossref, target_obj, target_crossref, scale_factor=1.0, reference_scale=None)`

Run all four matching strategies in order and store the result in `self.mhclo_line`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `focus_obj` | `bpy.types.Object` | — | The clothes (or bodypart) mesh object whose vertex is being matched |
| `focus_vert_index` | int | — | Index of the clothes vertex to match |
| `focus_crossref` | `MeshCrossRef` | — | Cross-reference tables for `focus_obj` |
| `target_obj` | `bpy.types.Object` | — | The base-mesh object to match against |
| `target_crossref` | `MeshCrossRef` | — | Cross-reference tables for `target_obj` (must be built with `build_faces_by_group_reference=True` for EXTENDED_FACE strategy) |
| `scale_factor` | float | `1.0` | Divisor applied to the offset displacement to normalise units |
| `reference_scale` | any | `None` | Reserved for future scale data; currently unused |

**Returns:** `None` (results are stored in instance attributes).

**Raises:**
- `ValueError` if `focus_vert_index` does not belong to any vertex group.
- `ValueError` if the vertex group name does not exist on `target_obj`.
- `ValueError` if all four strategies fail to find a match.

---

## Examples

### Match every vertex of a clothes object and collect MHCLO lines

```python
import bpy
from mpfb.entities.meshcrossref import MeshCrossRef
from mpfb.entities.clothes.mhclo import Mhclo
from mpfb.entities.clothes.vertexmatch import VertexMatch

clothes_obj = bpy.data.objects["MyShirt"]
basemesh_obj = bpy.data.objects["Human"]

# Build cross-reference tables; EXTENDED_FACE requires face-per-group tables
clothes_xref  = MeshCrossRef(clothes_obj, build_faces_by_group_reference=True)
basemesh_xref = MeshCrossRef(basemesh_obj, build_faces_by_group_reference=True)

mhclo = Mhclo()
mhclo.name = "my_shirt"

for vert_idx in range(len(clothes_obj.data.vertices)):
    vm = VertexMatch(
        clothes_obj, vert_idx, clothes_xref,
        basemesh_obj, basemesh_xref
    )
    mhclo.verts[vert_idx] = vm.mhclo_line

print(f"Matched {len(mhclo.verts)} vertices")
```

### Inspect the strategy used for each vertex

```python
for vert_idx in range(len(clothes_obj.data.vertices)):
    vm = VertexMatch(
        clothes_obj, vert_idx, clothes_xref,
        basemesh_obj, basemesh_xref
    )
    print(f"Vertex {vert_idx}: strategy={vm.final_strategy}")
```
