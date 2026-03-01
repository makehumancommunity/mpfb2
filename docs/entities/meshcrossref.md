# MeshCrossRef

## Overview

`MeshCrossRef` builds and holds a suite of cross-reference lookup tables for a mesh object, enabling efficient spatial and topological queries without repeated iteration over mesh data. 

The primary use case is being the cornerstone of the clothes creation process. There, one MeshCrossRef will hold lookup tables for the basemesh, and another for the clothes item. 

The key data it exposes includes:

- **numpy arrays** indexed by vertex, face, or edge index (coordinates, adjacency, group membership, face centres, normals).
- **`mathutils.KDTree` objects** for fast nearest-neighbour lookups against vertex coordinates and face median points.

**Modifier stripping on construction:** When `after_modifiers=True` (the default), the constructor makes a temporary copy of the mesh object and removes any `MASK` and `SUBSURF` modifiers from the copy before extracting geometry. This ensures that the vertex count of the arrays matches the basemesh rather than the modifier-evaluated result. The temporary copy is deleted once all tables are built.

**Optional caching:** Individual numpy arrays can be serialized to `.npy` files in a user-supplied directory. Pass `write_cache=True` to save on first construction and `read_cache=True` to restore on subsequent calls, avoiding expensive recomputation.

**Optional `faces_by_group` and per-group KDTrees:** Building the face-per-group tables requires iterating over every vertex's group membership for every face, which is significantly more expensive than the other tables. This step is skipped by default and must be requested explicitly via the `build_faces_by_group_reference` parameter.

## Source

`src/mpfb/entities/meshcrossref.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `numpy` | Array construction, file-based cache serialisation |
| `mathutils` | `KDTree` spatial index objects |
| `MeshService` | Extraction of vertex/face/edge arrays and KDTree from a Blender mesh object |
| `ObjectService` | Linking the temporary modifier-stripped copy and deleting it after construction |
| `LogService` | Logging via `LogService.get_logger("entities.meshcrossref")` |

## Attributes

The following attributes are set by the constructor and are the primary interface for callers.

| Attribute | Type | Description |
|-----------|------|-------------|
| `vertex_coordinates` | ndarray (V×3) | x, y, z coordinate of each vertex |
| `vertices_by_face` | ndarray (F×N) | vertex indices for each face |
| `vertices_by_edge` | ndarray (E×2) | vertex indices for each edge |
| `vertices_by_group` | list of ndarray | sorted unique vertex indices for each vertex group |
| `faces_by_vertex` | object ndarray (V,) | per-vertex array of face indices that use it (variable length) |
| `edges_by_vertex` | object ndarray (V,) | per-vertex array of edge indices that use it (variable length) |
| `face_neighbors` | object ndarray (F,) | per-face array of neighbouring face indices (variable length) |
| `face_median_points` | list of ndarray (3,) | centre point of each face |
| `face_normals` | list of ndarray (3,) | face normal shifted by the face median point |
| `vertex_coordinates_kdtree` | `mathutils.kdtree.KDTree` | spatial index over vertex coordinates |
| `face_median_points_kdtree` | `mathutils.kdtree.KDTree` | spatial index over face centre points |
| `face_median_points_by_group_kdtrees` | list of `KDTree` | one KDTree per vertex group, built only when `build_faces_by_group_reference=True` |
| `faces_by_group` | list of ndarray | sorted unique face indices per vertex group; populated only when `build_faces_by_group_reference=True` |
| `group_index_to_group_name` | list of str | maps group index → group name |
| `group_name_to_group_index` | dict str→int | maps group name → group index |
| `vertices_without_group` | ndarray | sorted vertex indices that belong to no vertex group |
| `vertices_with_multiple_groups` | ndarray | sorted vertex indices that belong to more than one vertex group |
| `cache_dir` | str or None | cache directory path as supplied to the constructor |
| `write_cache` | bool | whether cache writes are enabled |
| `read_cache` | bool | whether cache reads are enabled |
| `world_coordinates` | bool | whether coordinates are in world space (stored for caller reference) |

## Public API

### `__init__(mesh_object, after_modifiers=True, build_faces_by_group_reference=False, cache_dir=None, write_cache=False, read_cache=False, world_coordinates=True)`

Construct cross-reference tables for the given mesh object.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The Blender mesh object to analyse |
| `after_modifiers` | `bool` | `True` | If `True`, strip `MASK` and `SUBSURF` modifiers from a temporary copy before extracting geometry |
| `build_faces_by_group_reference` | `bool` | `False` | If `True`, also build `faces_by_group` and `face_median_points_by_group_kdtrees` (expensive) |
| `cache_dir` | `str` | `None` | Directory path for `.npy` cache files; created automatically if absent |
| `write_cache` | `bool` | `False` | Serialise computed arrays to `cache_dir` after building |
| `read_cache` | `bool` | `False` | Load arrays from `cache_dir` instead of computing them when cache files exist |
| `world_coordinates` | `bool` | `True` | Passed through to `MeshService` when extracting vertex coordinates |

---

### `read_array_from_cache(cache_file_name)`

Read a numpy array from the cache directory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `cache_file_name` | `str` | — | Filename (basename only) of the `.npy` cache file |

**Returns:** `numpy.ndarray` if the file exists and caching is enabled; `None` if `cache_dir` is not set, `read_cache` is `False`, the directory does not exist, or the file is absent.

---

### `write_array_to_cache(cache_file_name, numpy_array)`

Serialise a numpy array to the cache directory as a `.npy` file.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `cache_file_name` | `str` | — | Filename (basename only) for the cache file |
| `numpy_array` | `numpy.ndarray` | — | Array to save |

**Returns:** `None`.

If `cache_dir` is not set or `write_cache` is `False`, the call is a no-op. If the cache directory does not yet exist it is created. If a file with the same name already exists it is removed before the new file is written.

---

## Examples

### Basic construction

```python
import bpy
from mpfb.entities.meshcrossref import MeshCrossRef

mesh_obj = bpy.context.active_object  # a basemesh object
xref = MeshCrossRef(mesh_obj)

print("Vertex count:", len(xref.vertex_coordinates))
print("Face count:", len(xref.vertices_by_face))
```

### Spatial query — N closest vertices

```python
import bpy
from mpfb.entities.meshcrossref import MeshCrossRef

mesh_obj = bpy.context.active_object
xref = MeshCrossRef(mesh_obj)

query_point = (0.0, 0.0, 0.0)
n_results = 5
hits = xref.vertex_coordinates_kdtree.find_n(query_point, n_results)

for location, index, distance in hits:
    print(f"Vertex {index}: distance={distance:.4f}, coord={location}")
```

### With caching

```python
import bpy, os
from mpfb.entities.meshcrossref import MeshCrossRef

mesh_obj = bpy.context.active_object
cache_path = os.path.join("/tmp", "mpfb_cache", mesh_obj.name)

# First call: compute tables and save to disk
xref = MeshCrossRef(mesh_obj, cache_dir=cache_path, write_cache=True)

# Subsequent calls: load from disk instead of recomputing
xref = MeshCrossRef(mesh_obj, cache_dir=cache_path, read_cache=True)
```
