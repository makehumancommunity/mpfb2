# MeshService

## Overview

MeshService provides static methods for working with meshes, vertex groups, weights, and related spatial operations in MPFB. It complements ObjectService by focusing on mesh-specific operations rather than general object management.

The service covers several key areas: **mesh creation** (creating mesh objects from vertex/face data), **vertex group operations** (creating groups, finding vertices within groups), **UV map handling** (reading and writing UV coordinates), **spatial queries** (KDTree-based proximity searches), and **data extraction** (exporting mesh geometry as numpy arrays).

A notable feature is the KDTree support, which enables efficient nearest-neighbor searches between meshes. This is essential for operations like clothes fitting, where MPFB needs to find corresponding vertices between different meshes.

MeshService also provides cross-reference utilities through the `MeshCrossRef` entity, which builds efficient lookup tables for vertices, faces, and vertex groups.

All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/meshservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.meshservice")` |
| `ObjectService` | Object linking operations |

## Public API

### Mesh Creation

#### create_mesh_object(vertices, edges, faces, vertex_groups=None, name="sample_object", link=True)

Create a new mesh object from geometry data.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `vertices` | `list` | — | List of vertex coordinates as `(x, y, z)` tuples |
| `edges` | `list` | — | List of edges as `(v1, v2)` tuples |
| `faces` | `list` | — | List of faces as vertex index tuples |
| `vertex_groups` | `dict` | `None` | Dict mapping group names to lists of `[vertex_index, weight]` pairs |
| `name` | `str` | `"sample_object"` | Name for the new object |
| `link` | `bool` | `True` | Whether to link the object to the current collection |

**Returns:** `bpy.types.Object` — The newly created mesh object.

The mesh data block is named `<name>_mesh`.

---

#### create_sample_object(name="sample_object", link=True)

Create a simple test mesh with four quad faces.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | `"sample_object"` | Name for the object |
| `link` | `bool` | `True` | Whether to link the object |

**Returns:** `bpy.types.Object` — A 3x3 grid plane mesh with predefined vertex groups (`left`, `right`, `mid`, `all`).

Useful for testing vertex group and mesh operations.

---

### Vertex Group Operations

#### create_vertex_group(mesh_object, vertex_group_name, verts_and_weights, nuke_existing_group=False)

Create a vertex group and populate it with weighted vertices.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The mesh object |
| `vertex_group_name` | `str` | — | Name for the vertex group |
| `verts_and_weights` | `list` | — | List of `[vertex_index, weight]` pairs |
| `nuke_existing_group` | `bool` | `False` | Remove existing group with same name |

**Returns:** None

If a group with the same name exists and `nuke_existing_group` is `False`, vertices are added to the existing group.

---

#### find_vertices_in_vertex_group(mesh_object, vertex_group_name)

Find all vertices belonging to a vertex group.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The mesh object |
| `vertex_group_name` | `str` | — | Name of the vertex group |

**Returns:** `list` — List of `[vertex_index, weight]` pairs.

Returns an empty list if the vertex group doesn't exist.

---

#### find_faces_in_vertex_group(mesh_object, vertex_group_name)

Find all faces where every vertex belongs to a vertex group.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The mesh object |
| `vertex_group_name` | `str` | — | Name of the vertex group |

**Returns:** `list[int]` — List of face indices.

A face is included only if all of its vertices are members of the specified group.

---

#### select_all_vertices_in_vertex_group_for_active_object(vertex_group_name, deselect_other=True)

Select vertices in a vertex group in edit mode.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `vertex_group_name` | `str` | — | Name of the vertex group |
| `deselect_other` | `bool` | `True` | Deselect all other vertices first |

**Returns:** None

The object must be active. Switches to vertex selection mode before selecting.

---

### UV Map Operations

#### get_uv_map_names(mesh_object)

List all UV map names on a mesh.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The mesh object |

**Returns:** `list[str]` — List of UV map names.

---

#### get_uv_map_as_dict(mesh_object, uv_map_name, only_include_vertex_group=None)

Export UV coordinates as a dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The mesh object |
| `uv_map_name` | `str` | — | Name of the UV map |
| `only_include_vertex_group` | `str` | `None` | Only include faces in this vertex group |

**Returns:** `dict` — Nested dictionary: `{face_index: {loop_index: [u, v], ...}, ...}`

Returns an empty dict if the UV map doesn't exist.

---

#### add_uv_map_from_dict(mesh_object, uv_map_name, uv_map_as_dict)

Create a UV map from a dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The mesh object |
| `uv_map_name` | `str` | — | Name for the UV map |
| `uv_map_as_dict` | `dict` | — | UV data in the format from `get_uv_map_as_dict` |

**Returns:** None

If a UV map with the same name exists, it is replaced. Faces not in the dictionary receive scaled-down default coordinates.

---

### Spatial Queries (KDTree)

#### get_kdtree(mesh_object, balance=True, limit_to_vertex_group=None, after_modifiers=False, world_coordinates=True)

Build a KDTree from mesh vertices for spatial lookups.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The mesh object |
| `balance` | `bool` | `True` | Balance the tree after construction |
| `limit_to_vertex_group` | `str` | `None` | Only include vertices in this group |
| `after_modifiers` | `bool` | `False` | Use evaluated mesh (after modifiers) |
| `world_coordinates` | `bool` | `True` | Transform to world coordinates |

**Returns:** `mathutils.kdtree.KDTree` — The constructed KDTree.

**Raises:** `ValueError` — If `limit_to_vertex_group` is specified but doesn't exist.

The KDTree enables O(log n) nearest-neighbor searches, essential for fitting operations.

---

#### closest_vertices(focus_obj, focus_vert_idx, target_obj, target_obj_kdtree, number_of_matches=1, world_coordinates=True)

Find the closest vertex(es) on a target mesh to a given vertex.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `focus_obj` | `bpy.types.Object` | — | The source mesh object |
| `focus_vert_idx` | `int` | — | Index of the vertex to match |
| `target_obj` | `bpy.types.Object` | — | The target mesh object |
| `target_obj_kdtree` | `mathutils.kdtree.KDTree` | — | Pre-built KDTree for target |
| `number_of_matches` | `int` | `1` | Number of nearest vertices to find |
| `world_coordinates` | `bool` | `True` | Use world coordinates |

**Returns:** `list` — For single match: `[(location, index, distance)]`. For multiple: list of such tuples.

**Raises:** `ValueError` — If objects are `None`, KDTree is `None`, or objects have non-unit scales.

---

### Data Extraction (Numpy)

#### get_vertex_coordinates_as_numpy_array(mesh_object, after_modifiers=False, world_coordinates=True)

Export vertex coordinates as a numpy array.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The mesh object |
| `after_modifiers` | `bool` | `False` | Use evaluated mesh |
| `world_coordinates` | `bool` | `True` | Transform to world coordinates |

**Returns:** `numpy.ndarray` — Shape `(num_vertices, 3)`, dtype `float32`.

---

#### get_faces_as_numpy_array(mesh_object)

Export face vertex indices as a numpy array.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The mesh object |

**Returns:** `numpy.ndarray` — Shape `(num_faces, verts_per_face)`, dtype `uint32`.

**Raises:** `ValueError` — If faces have different vertex counts (mixed tris/quads).

---

#### get_edges_as_numpy_array(mesh_object)

Export edge vertex indices as a numpy array.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The mesh object |

**Returns:** `numpy.ndarray` — Shape `(num_edges, 2)`, dtype `uint32`.

---

### Cross References

#### get_mesh_cross_references(mesh_object, after_modifiers=True, build_faces_by_group_reference=False)

Build a cross-reference container for efficient mesh queries.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The mesh object |
| `after_modifiers` | `bool` | `True` | Use evaluated mesh |
| `build_faces_by_group_reference` | `bool` | `False` | Build face-to-group lookup |

**Returns:** `MeshCrossRef` — A container with precomputed lookup tables.

The `MeshCrossRef` entity provides efficient access to vertex-to-face mappings, group memberships, and other relationships.

---

## Examples

### Creating a Mesh from Geometry

```python
from mpfb.services.meshservice import MeshService

# Define a simple pyramid
vertices = [
    (0, 0, 0),     # 0: base center
    (1, 0, 0),     # 1: base front-right
    (0, 1, 0),     # 2: base back-left
    (-1, 0, 0),    # 3: base front-left
    (0, -1, 0),    # 4: base back-right
    (0, 0, 1),     # 5: apex
]

faces = [
    (0, 1, 5),
    (0, 2, 5),
    (0, 3, 5),
    (0, 4, 5),
    (1, 2, 3, 4),  # base
]

vertex_groups = {
    "apex": [[5, 1.0]],
    "base": [[0, 1.0], [1, 1.0], [2, 1.0], [3, 1.0], [4, 1.0]],
}

pyramid = MeshService.create_mesh_object(
    vertices, [], faces,
    vertex_groups=vertex_groups,
    name="Pyramid"
)
```

### Working with Vertex Groups

```python
from mpfb.services.meshservice import MeshService

# Get vertices in a group with their weights
verts = MeshService.find_vertices_in_vertex_group(mesh_obj, "Body")
for vert_idx, weight in verts:
    print(f"Vertex {vert_idx}: weight {weight}")

# Get faces entirely within a group
face_indices = MeshService.find_faces_in_vertex_group(mesh_obj, "Face")
print(f"Found {len(face_indices)} faces in 'Face' group")

# Create a new vertex group
MeshService.create_vertex_group(
    mesh_obj, "Selected",
    [[0, 1.0], [1, 0.8], [2, 0.5]],
    nuke_existing_group=True
)
```

### Finding Nearest Vertices (Clothes Fitting)

```python
from mpfb.services.meshservice import MeshService

# Build KDTree for the basemesh
basemesh_kdtree = MeshService.get_kdtree(
    basemesh,
    after_modifiers=True,
    world_coordinates=True
)

# For each clothes vertex, find the nearest basemesh vertex
for vert_idx in range(len(clothes_obj.data.vertices)):
    matches = MeshService.closest_vertices(
        clothes_obj, vert_idx,
        basemesh, basemesh_kdtree,
        number_of_matches=3
    )

    # matches is a list of (location, index, distance) tuples
    nearest_location, nearest_idx, distance = matches[0]
    print(f"Clothes vert {vert_idx} -> Basemesh vert {nearest_idx} (dist: {distance:.4f})")
```

### UV Map Operations

```python
from mpfb.services.meshservice import MeshService

# List UV maps
uv_names = MeshService.get_uv_map_names(mesh_obj)
print(f"UV maps: {uv_names}")

# Export UV coordinates
uv_dict = MeshService.get_uv_map_as_dict(mesh_obj, "UVMap")

# Export only for faces in a vertex group
face_uv_dict = MeshService.get_uv_map_as_dict(
    mesh_obj, "UVMap",
    only_include_vertex_group="Face"
)

# Copy UVs to another object
MeshService.add_uv_map_from_dict(other_mesh, "CopiedUV", uv_dict)
```

### Exporting to Numpy

```python
from mpfb.services.meshservice import MeshService
import numpy as np

# Get vertex positions as numpy array
verts = MeshService.get_vertex_coordinates_as_numpy_array(
    mesh_obj,
    after_modifiers=True,
    world_coordinates=False
)
print(f"Vertices shape: {verts.shape}")  # (num_verts, 3)

# Get faces
faces = MeshService.get_faces_as_numpy_array(mesh_obj)
print(f"Faces shape: {faces.shape}")  # (num_faces, verts_per_face)

# Calculate bounding box
min_coords = verts.min(axis=0)
max_coords = verts.max(axis=0)
print(f"Bounding box: {min_coords} to {max_coords}")
```

### Using Mesh Cross References

```python
from mpfb.services.meshservice import MeshService

# Build cross references for efficient lookups
xref = MeshService.get_mesh_cross_references(
    mesh_obj,
    after_modifiers=True,
    build_faces_by_group_reference=True
)

# Access precomputed data
# (Specific usage depends on MeshCrossRef implementation)
```

### Complete Workflow: Transferring Weights

```python
from mpfb.services.meshservice import MeshService
from mpfb.services.objectservice import ObjectService

def transfer_weights(source_obj, target_obj, group_name):
    """Transfer vertex group weights from source to target mesh."""

    # Check if source has the group
    if not ObjectService.has_vertex_group(source_obj, group_name):
        print(f"Source doesn't have group '{group_name}'")
        return

    # Get source vertices and weights
    source_verts = MeshService.find_vertices_in_vertex_group(source_obj, group_name)

    # Build KDTree for source
    source_kdtree = MeshService.get_kdtree(source_obj)

    # For each target vertex, find nearest source vertex and get its weight
    target_weights = []
    for vert in target_obj.data.vertices:
        matches = MeshService.closest_vertices(
            target_obj, vert.index,
            source_obj, source_kdtree,
            number_of_matches=1
        )
        _, source_idx, _ = matches[0]

        # Find weight of nearest source vertex
        weight = 0.0
        for vidx, w in source_verts:
            if vidx == source_idx:
                weight = w
                break

        if weight > 0:
            target_weights.append([vert.index, weight])

    # Create the group on target
    MeshService.create_vertex_group(
        target_obj, group_name, target_weights,
        nuke_existing_group=True
    )
    print(f"Transferred {len(target_weights)} weighted vertices")
```
