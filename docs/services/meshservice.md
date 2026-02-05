# MeshService

MeshService provides static methods for working with meshes, vertex groups, weights, and related operations. It offers mesh creation, vertex and face queries, UV map manipulation, KDTree spatial lookups, and numpy array extraction.

## Source

`src/mpfb/services/meshservice.py`

## Dependencies

- `LogService` — logging
- `ObjectService` — object linking operations

## Public API

### create_mesh_object(vertices, edges, faces, vertex_groups=None, name="sample_object", link=True)

Create a new mesh object from vertices, edges, and faces with optional vertex groups.

### create_sample_object(name="sample_object", link=True)

Create a sample plane mesh with four faces.

### find_vertices_in_vertex_group(mesh_object, vertex_group_name)

Find all vertices in a vertex group, returning a list of (index, weight) tuples.

### find_faces_in_vertex_group(mesh_object, vertex_group_name)

Find all faces where every vertex belongs to the given vertex group.

### get_uv_map_names(mesh_object)

List all UV map names on a mesh object.

### get_uv_map_as_dict(mesh_object, uv_map_name, only_include_vertex_group=None)

Return UV coordinates as a dict, optionally filtered by vertex group.

### add_uv_map_from_dict(mesh_object, uv_map_name, uv_map_as_dict)

Create a new UV map from a dict and add it to the mesh object.

### create_vertex_group(mesh_object, vertex_group_name, verts_and_weights, nuke_existing_group=False)

Create a vertex group and populate it with vertex indices and weights.

### get_kdtree(mesh_object, balance=True, limit_to_vertex_group=None, after_modifiers=False, world_coordinates=True)

Build a KDTree from a mesh object's vertices for spatial lookups.

### closest_vertices(focus_obj, focus_vert_idx, target_obj, target_obj_kdtree, number_of_matches=1, world_coordinates=True)

Find the closest vertex or vertices on a target object for a given focus vertex.

### get_vertex_coordinates_as_numpy_array(mesh_object, after_modifiers=False, world_coordinates=True)

Get vertex coordinates as a numpy array.

### get_faces_as_numpy_array(mesh_object)

Get face data as a numpy array.

### get_edges_as_numpy_array(mesh_object)

Get edge data as a numpy array.

### get_mesh_cross_references(mesh_object, after_modifiers=True, build_faces_by_group_reference=False)

Build a cross-reference container for a mesh object with vertex, face, and group mappings.

### select_all_vertices_in_vertex_group_for_active_object(vertex_group_name, deselect_other=True)

Select all vertices in the specified vertex group for the active object.

## Example

```python
from mpfb.services.meshservice import MeshService

verts = MeshService.find_vertices_in_vertex_group(mesh_obj, "Body")
kdtree = MeshService.get_kdtree(mesh_obj)
coords = MeshService.get_vertex_coordinates_as_numpy_array(mesh_obj)
```
