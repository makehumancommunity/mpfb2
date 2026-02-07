# ClothesService

## Overview

ClothesService provides static methods for managing and manipulating clothes objects in relation to a MakeHuman basemesh. Its primary responsibility is **fitting clothes** to a character by translating and scaling each clothes vertex according to a mapping defined in an MHCLO file. Each clothes vertex is mapped to three basemesh vertices with barycentric weights and an offset vector, allowing clothes to deform as the character's shape changes.

A second major responsibility is **geometry hiding**. When a piece of clothing covers part of the body, the underlying basemesh faces can be hidden via "delete groups" — vertex groups combined with MASK modifiers. ClothesService creates and updates these groups, applying a conservative mask algorithm that removes outlier vertices to avoid visual artefacts at group edges.

The service also handles **weight interpolation** for rigging: when a rig is present, bone weights are transferred from the basemesh to the clothes mesh using the MHCLO vertex mapping. Custom weight overrides can be loaded from sidecar files. For the **MakeClothes** workflow, the service can validate whether a mesh is suitable for use as clothes and can generate MHCLO data from scratch by matching a clothes mesh to the basemesh. All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/clothesservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.clothesservice")` |
| `ObjectService` | Blender object operations, vertex group queries, face/vertex tables |
| `MeshService` | Finding vertices belonging to a vertex group |
| `LocationService` | Resolving user cache paths |
| `AssetService` | Locating asset files by path fragment |
| `RigService` | Rig identification, weight loading, armature modifier setup |
| `Mhclo` | MHCLO entity for loading and representing clothes mapping data |
| `Rig` | Rig entity for sub-rig creation |
| `VertexMatch` | Vertex matching algorithm used during MHCLO creation |
| `MeshCrossRef` | Cross-reference data structure for mesh vertices, faces, and groups |
| `GeneralObjectProperties` | Reading/writing custom object properties (asset source, scale factor, UUID) |

## Constants

### CLOTHES_REFERENCE_SCALE

A module-level dictionary mapping body part names to vertex index pairs used for computing reference scales. Each entry defines six vertex indices (`xmin`, `xmax`, `ymin`, `ymax`, `zmin`, `zmax`) that bound the body part in world space. The distance between these vertices provides a baseline for scaling clothes offsets during the MakeClothes matching process.

Body parts covered: `Body`, `Head`, `Teeth`, `Torso`, `Arm`, `Hand`, `Leg`, `Foot`, `Eye`, `Genital`.

## Public API

### Clothes Fitting

#### fit_clothes_to_human(clothes, basemesh, mhclo=None, set_parent=True)

Move clothes vertices so they fit the current shape of the basemesh. The method creates a temporary "from mix" shape key on the basemesh to capture the combined effect of all current shape keys, then repositions each clothes vertex using the MHCLO mapping data (three basemesh vertex references, barycentric weights, and a scaled offset). If the clothes mesh has shape keys, the Basis shape key is updated via edit mode. When `mhclo` is not provided, it is loaded automatically from the asset source stored in the clothes object's custom properties.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `clothes` | `bpy.types.Object` | — | The clothes mesh object to refit |
| `basemesh` | `bpy.types.Object` | — | The basemesh to fit clothes to |
| `mhclo` | `Mhclo` | `None` | Pre-loaded MHCLO data; auto-loaded from object properties if `None` |
| `set_parent` | `bool` | `True` | Whether to parent the clothes to the basemesh or its rig |

**Returns:** None

**Raises:** `ValueError` if basemesh or clothes is `None`, basemesh is not a valid basemesh, MHCLO vertex info is missing, or asset source metadata is insufficient. `IOError` if the MHCLO file cannot be found on disk.

---

#### get_reference_scale(basemesh, body_part_reference="Torso")

Compute a reference scale dictionary from a basemesh, measuring the distances between specific vertex pairs defined in `CLOTHES_REFERENCE_SCALE`. The basemesh is temporarily duplicated with MASK and SUBSURF modifiers removed, then evaluated to get post-modifier vertex positions. The resulting scale values are normalized by the basemesh's scale factor.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh to measure |
| `body_part_reference` | `str` | `"Torso"` | Key in `CLOTHES_REFERENCE_SCALE` to use for measurements |

**Returns:** `dict` — A dictionary with keys `x_scale`, `y_scale`, `z_scale` (float distances) plus the vertex indices from the selected body part reference.

---

### Delete Groups

#### update_delete_group(mhclo, basemesh, replace_delete_group=False, delete_group_name=None, add_modifier=True, skip_if_empty_delete_group=True)

Create or update a "delete" vertex group on the basemesh to hide geometry underneath clothes. The group is populated with vertex indices from the MHCLO's delete vertex list, filtered through a conservative mask algorithm that excludes vertices on partially-affected face boundaries. A MASK modifier is added to the basemesh if one does not already exist for this group.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mhclo` | `Mhclo` | — | The MHCLO object containing delete vertex data |
| `basemesh` | `bpy.types.Object` | — | The basemesh to add the delete group to |
| `replace_delete_group` | `bool` | `False` | Remove any existing group with the same name before creating |
| `delete_group_name` | `str` | `None` | Custom name for the group; uses MHCLO's `delete_group` or `"Delete"` if `None` |
| `add_modifier` | `bool` | `True` | Whether to add a MASK modifier for the group |
| `skip_if_empty_delete_group` | `bool` | `True` | Return immediately if the MHCLO has no delete vertices |

**Returns:** None

---

#### create_new_delete_group(basemesh, clothes, mhclo, group_name="Delete")

Create a new delete group on the basemesh based on which vertices are covered by the clothes mesh. Unlike `update_delete_group` which reads pre-defined delete vertices from the MHCLO, this method derives the covered area from the MHCLO vertex matchings: it collects all basemesh vertices referenced by the matchings, then extends the set to include all vertices belonging to any face touched by those vertices.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh object |
| `clothes` | `bpy.types.Object` | — | The clothes object matching the MHCLO |
| `mhclo` | `Mhclo` | — | A populated MHCLO with vertex matchings |
| `group_name` | `str` | `"Delete"` | Name for the new vertex group |

**Returns:** `bpy.types.VertexGroup` — The newly created delete group.

**Raises:** `ValueError` if any argument is `None`, objects are not meshes, or the MHCLO has no matchings or mismatched vertex counts.

---

### Rigging and Weights

#### interpolate_weights(basemesh, clothes, rig, mhclo)

Copy rigging weights from the basemesh to the clothes mesh by interpolating through the MHCLO vertex mapping. For each clothes vertex, the method looks up the three mapped basemesh vertices, multiplies each basemesh vertex's bone group weights by the MHCLO barycentric weight, and accumulates the result. Interpolated weights below `0.001` are discarded for performance. The method also carries over `DEF-` (Rigify deform) and `mhmask-` vertex groups.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh with source vertex weights |
| `clothes` | `bpy.types.Object` | — | The clothes mesh to receive interpolated weights |
| `rig` | `bpy.types.Object` | — | The armature whose bone names define the vertex groups |
| `mhclo` | `Mhclo` | — | MHCLO mapping data linking clothes vertices to basemesh vertices |

**Returns:** None

---

#### set_up_rigging(basemesh, clothes, rig, mhclo, *, interpolate_weights=True, import_subrig=True, import_weights=True)

Set up the full rigging pipeline for a clothes object: optionally load a custom sub-rig from an `.mpfbskel` sidecar file, parent the clothes to the rig (or sub-rig), interpolate weights, load custom weight overrides, and ensure the armature modifier is in place.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh object |
| `clothes` | `bpy.types.Object` | — | The clothes mesh to rig |
| `rig` | `bpy.types.Object` | — | The main armature object |
| `mhclo` | `Mhclo` | — | MHCLO mapping data |
| `interpolate_weights` | `bool` | `True` | Whether to interpolate weights from the basemesh |
| `import_subrig` | `bool` | `True` | Whether to import a custom sub-rig if available |
| `import_weights` | `bool` | `True` | Whether to load custom weight files |

**Returns:** None

---

#### load_custom_weights(clothes, armature_object, subrig, mhclo)

Load custom weight files for the given clothes and rig. The method tries loading weights from several sidecar files: the base weights file (no suffix), a "force" file for non-standard mask groups, and a rig-type-specific file determined by `RigService.identify_rig`. For Rigify generated rigs, the rig type is mapped back to the base Rigify type.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `clothes` | `bpy.types.Object` | — | The clothes mesh to load weights onto |
| `armature_object` | `bpy.types.Object` | — | The main armature object |
| `subrig` | `bpy.types.Object` or `None` | — | The sub-rig armature, or `None` if not applicable |
| `mhclo` | `Mhclo` | — | MHCLO object used to derive weight file paths |

**Returns:** None

---

#### interpolate_vertex_group_from_basemesh_to_clothes(basemesh, clothes_object, vertex_group_name, match_cutoff=0.3, mhclo_full_path=None)

Interpolate a single vertex group from the basemesh to the clothes object. The method loads the MHCLO file, finds which clothes vertices are mapped to basemesh vertices that belong to the specified vertex group, and creates a corresponding vertex group on the clothes with those vertices at weight `1.0`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh with the source vertex group |
| `clothes_object` | `bpy.types.Object` | — | The clothes object to add the group to |
| `vertex_group_name` | `str` | — | Name of the vertex group to interpolate |
| `match_cutoff` | `float` | `0.3` | Cutoff value for matching vertices |
| `mhclo_full_path` | `str` | `None` | Path to the MHCLO file; auto-resolved if `None` |

**Returns:** `bpy.types.VertexGroup` — The newly created vertex group on the clothes.

---

### Asset Management

#### find_clothes_absolute_path(clothes_object)

Find the absolute file path to the MHCLO asset of a clothes object by reading the `asset_source` and `object_type` custom properties and resolving them via `AssetService`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `clothes_object` | `bpy.types.Object` | — | The clothes object to look up |

**Returns:** `str` or `None` — The absolute path to the MHCLO file, or `None` if the properties are missing.

---

#### set_makeclothes_object_properties_from_mhclo(clothes_object, mhclo, delete_group_name=None)

Update a clothes object's MakeClothes custom properties (author, description, license, name, tag, z_depth, delete_group, homepage) from the metadata stored in an MHCLO object.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `clothes_object` | `bpy.types.Object` | — | The clothes object to update |
| `mhclo` | `Mhclo` | — | The MHCLO object containing metadata |
| `delete_group_name` | `str` | `None` | Override value for the delete group property |

**Returns:** None

---

### MakeClothes

#### mesh_is_valid_as_clothes(mesh_object, basemesh)

Validate whether a mesh object can be used as clothes for the given basemesh. Performs a series of checks and returns a detailed report dictionary. The checks include: valid mesh type, has vertices, has vertex groups, each vertex in exactly one group, all vertices belong to faces, all clothes groups exist on the basemesh, and matching scale.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The candidate clothes mesh |
| `basemesh` | `bpy.types.Object` | — | The basemesh to validate against |

**Returns:** `dict` — A validation report with keys: `is_valid_object` (bool), `has_any_vertices` (bool), `has_any_vgroups` (bool), `all_verts_have_max_one_vgroup` (bool), `all_verts_have_min_one_vgroup` (bool), `all_verts_belong_to_faces` (bool), `clothes_groups_exist_on_basemesh` (bool), `objs_same_scale` (bool), `all_checks_ok` (bool), and `warnings` (list of strings).

---

#### create_mhclo_from_clothes_matching(basemesh, clothes, properties_dict=None, delete_group=None)

Create an MHCLO object from scratch by matching clothes vertices to the basemesh. For each clothes vertex, a `VertexMatch` is computed that finds the three closest basemesh vertices, their barycentric weights, and the offset. The result is a fully populated MHCLO object that can be saved to a file. If a delete group name is specified and exists on the basemesh, the corresponding vertices are included in the MHCLO's delete list.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh to match against |
| `clothes` | `bpy.types.Object` | — | The clothes mesh whose vertices will be matched |
| `properties_dict` | `dict` | `None` | Optional dictionary of MHCLO metadata properties to set |
| `delete_group` | `str` | `None` | Name of a vertex group on the basemesh to use as the delete group |

**Returns:** `Mhclo` — A populated MHCLO object with vertex matchings.

---

## Examples

### Fitting Clothes to a Character

```python
from mpfb.services.clothesservice import ClothesService
from mpfb.entities.clothes.mhclo import Mhclo

# Auto-fit: the MHCLO is loaded from the clothes object's properties
ClothesService.fit_clothes_to_human(clothes_obj, basemesh)

# Manual fit: provide a pre-loaded MHCLO
mhclo = Mhclo()
mhclo.load("/path/to/shirt.mhclo")
mhclo.clothes = clothes_obj
ClothesService.fit_clothes_to_human(clothes_obj, basemesh, mhclo=mhclo)
```

### Setting Up Delete Groups

```python
from mpfb.services.clothesservice import ClothesService

# Update a delete group from MHCLO data
ClothesService.update_delete_group(mhclo, basemesh, delete_group_name="Delete.shirt")

# Create a new delete group derived from clothes coverage
delete_group = ClothesService.create_new_delete_group(basemesh, clothes_obj, mhclo, group_name="Delete.pants")
```

### Rigging Clothes

```python
from mpfb.services.clothesservice import ClothesService

# Full rigging pipeline: weights, sub-rig, and custom weights
ClothesService.set_up_rigging(basemesh, clothes_obj, rig, mhclo)

# Interpolate weights only, skip sub-rig and custom weights
ClothesService.set_up_rigging(basemesh, clothes_obj, rig, mhclo,
                              import_subrig=False, import_weights=False)

# Interpolate a single vertex group (e.g. for proxy meshes)
ClothesService.interpolate_vertex_group_from_basemesh_to_clothes(
    basemesh, proxy_obj, "Delete.shirt"
)
```

### MakeClothes Workflow

```python
from mpfb.services.clothesservice import ClothesService

# Validate a mesh before creating MHCLO data
report = ClothesService.mesh_is_valid_as_clothes(my_clothes_mesh, basemesh)
if report["all_checks_ok"]:
    mhclo = ClothesService.create_mhclo_from_clothes_matching(
        basemesh, my_clothes_mesh,
        properties_dict={"name": "My Shirt", "author": "Me"},
        delete_group="Delete"
    )
else:
    for warning in report["warnings"]:
        print(f"Warning: {warning}")
```
