# ClothesService

ClothesService provides static methods for managing and manipulating clothes objects in relation to a basemesh. Key responsibilities include loading MHCLO objects, fitting clothes to the basemesh by translating and scaling vertices, interpolating vertex groups and weights, generating MHCLO data from existing meshes, and managing rigging for clothes assets.

## Source

`src/mpfb/services/clothesservice.py`

## Dependencies

- `LogService` — logging
- `ObjectService` — Blender object operations
- `MeshService` — mesh manipulation
- `LocationService` — path resolution
- `AssetService` — asset discovery
- `RigService` — rig management
- `Mhclo`, `Rig`, `VertexMatch`, `MeshCrossRef` — entity classes

## Public API

### fit_clothes_to_human(clothes, basemesh, mhclo=None, set_parent=True)

Move clothes vertices to fit the current basemesh shape using MHCLO mapping data.

### update_delete_group(mhclo, basemesh, replace_delete_group=False, delete_group_name=None, add_modifier=True, skip_if_empty_delete_group=True)

Create or update a delete group on the basemesh to hide geometry under clothes.

### find_clothes_absolute_path(clothes_object)

Find the absolute file path to the MHCLO asset of a clothes object.

### interpolate_vertex_group_from_basemesh_to_clothes(basemesh, clothes_object, vertex_group_name, match_cutoff=0.3, mhclo_full_path=None)

Interpolate a vertex group from the basemesh onto the clothes object.

### interpolate_weights(basemesh, clothes, rig, mhclo)

Copy rigging weights from the basemesh to the clothes object.

### set_up_rigging(basemesh, clothes, rig, mhclo, *, interpolate_weights=True, import_subrig=True, import_weights=True)

Set up weights and an optional custom sub-rig for clothes.

### load_custom_weights(clothes, armature_object, subrig, mhclo)

Load custom weights for clothes from the MHCLO weight files.

### set_makeclothes_object_properties_from_mhclo(clothes_object, mhclo, delete_group_name=None)

Update clothes object properties from MHCLO metadata.

### mesh_is_valid_as_clothes(mesh_object, basemesh)

Validate whether a mesh can be used as clothes for the given basemesh.

### create_mhclo_from_clothes_matching(basemesh, clothes, properties_dict=None, delete_group=None)

Create an MHCLO object by matching clothes vertices to the basemesh.

### get_reference_scale(basemesh, body_part_reference="Torso")

Get the reference scale from the basemesh for the specified body part.

### create_new_delete_group(basemesh, clothes, mhclo, group_name="Delete")

Create a delete group based on the clothes' coverage area on the basemesh.

## Example

```python
from mpfb.services.clothesservice import ClothesService

ClothesService.fit_clothes_to_human(clothes_obj, basemesh)
ClothesService.interpolate_weights(basemesh, clothes_obj, rig, mhclo)
ClothesService.update_delete_group(mhclo, basemesh)
```
