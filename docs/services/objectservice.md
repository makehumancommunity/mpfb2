# ObjectService

## Overview

ObjectService provides a comprehensive collection of static utility methods for managing and manipulating Blender objects within MPFB. It is one of the most heavily used services in the addon, handling everything from basic object creation to complex relationship queries.

The service's responsibilities fall into several categories: **object lifecycle management** (creation, linking, deletion), **selection and activation** (making objects active, deselecting), **type identification** (determining if an object is a basemesh, skeleton, clothes, etc.), **relationship queries** (finding parents, children, and siblings), and **file operations** (loading and saving Wavefront OBJ files).

ObjectService introduces the concept of MPFB object types, stored as custom properties on objects. These types include `Basemesh`, `Skeleton`, `Subrig`, `Proxymesh`, `Eyes`, `Clothes`, `Hair`, and others. Many methods use these types to identify and filter objects, making it easy to find all clothes attached to a character or locate the skeleton associated with a mesh.

The service also provides specialized methods for working with Rigify rigs, detecting whether an armature is a Rigify metarig or generated rig, and finding the relationship between them.

All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/objectservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.objectservice")` |
| `LocationService` | Resolving paths to base mesh OBJ and vertex group definitions |
| `GeneralObjectProperties` | Accessing MPFB custom properties on objects |
| `TargetService` | Shape key operations (imported at call time to avoid circular imports) |
| `MaterialService` | Material deletion (imported at call time to avoid circular imports) |

## Object Type Constants

MPFB uses custom properties to identify object types:

| Type | Description |
|------|-------------|
| `Basemesh` | The main human body mesh |
| `Skeleton` | The primary armature/rig |
| `Subrig` | Secondary armatures for clothes or accessories |
| `Proxymesh` / `Proxymeshes` | Body proxy meshes |
| `Eyes` | Eye meshes |
| `Eyelashes` | Eyelash meshes |
| `Eyebrows` | Eyebrow meshes |
| `Tongue` | Tongue mesh |
| `Teeth` | Teeth mesh |
| `Hair` | Hair mesh or particle system holder |
| `Clothes` | Clothing items |

## Public API

### Object Creation

#### random_name()

Generate a random string of 15 lowercase ASCII characters.

**Returns:** `str` — A random string suitable for use as a temporary object name.

---

#### create_blender_object_with_mesh(name="NewObject", parent=None, skip_linking=False)

Create a new mesh object with an empty mesh data block.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | `"NewObject"` | The name for the new object |
| `parent` | `bpy.types.Object` | `None` | Optional parent object |
| `skip_linking` | `bool` | `False` | If `True`, don't link to the current collection |

**Returns:** `bpy.types.Object` — The newly created mesh object.

The mesh data block is named `<name>Mesh`.

---

#### create_blender_object_with_armature(name="NewObject", parent=None)

Create a new armature object with an armature data block.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | `"NewObject"` | The name for the new object |
| `parent` | `bpy.types.Object` | `None` | Optional parent object |

**Returns:** `bpy.types.Object` — The newly created armature object.

The armature data block is named `<name>Armature`.

---

#### create_empty(name, empty_type="SPHERE", parent=None)

Create a new empty object.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The name for the empty object |
| `empty_type` | `str` | `"SPHERE"` | The empty display type (e.g., `"PLAIN_AXES"`, `"ARROWS"`, `"SPHERE"`) |
| `parent` | `bpy.types.Object` | `None` | Optional parent object |

**Returns:** `bpy.types.Object` — The newly created empty object.

---

#### link_blender_object(object_to_link, collection=None, parent=None)

Link an object to a collection and optionally set its parent.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `object_to_link` | `bpy.types.Object` | — | The object to link |
| `collection` | `bpy.types.Collection` | `None` | Target collection (defaults to current context collection) |
| `parent` | `bpy.types.Object` | `None` | Optional parent object |

**Returns:** None

---

### Object Deletion

#### delete_object(object_to_delete)

Safely delete a Blender object.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `object_to_delete` | `bpy.types.Object` | — | The object to delete |

**Returns:** None

Does nothing if the object is `None`.

---

#### delete_object_by_name(name)

Safely delete an object by its name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The name of the object to delete |

**Returns:** None

Does nothing if the name is empty or no object with that name exists.

---

### Selection and Activation

#### activate_blender_object(object_to_make_active, *, context=None, deselect_all=False)

Make an object selected and active.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `object_to_make_active` | `bpy.types.Object` | — | The object to activate |
| `context` | `bpy.types.Context` | `None` | Blender context (defaults to `bpy.context`) |
| `deselect_all` | `bool` | `False` | If `True`, deselect all other objects first |

**Returns:** None

---

#### select_object(obj)

Select an object and make it active, deselecting all others.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `obj` | `bpy.types.Object` | — | The object to select |

**Returns:** None

This is a convenience wrapper around `activate_blender_object` with `deselect_all=True`.

---

#### deselect_and_deactivate_all()

Ensure no object is selected or active.

**Returns:** None

Switches to Object mode if necessary and clears all selection state.

---

### Object Queries

#### object_name_exists(name)

Check if an object with the given name exists.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The name to check |

**Returns:** `bool` — `True` if an object with that name exists.

---

#### ensure_unique_name(desired_name)

Generate a unique object name by appending incrementing numbers if needed.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `desired_name` | `str` | — | The preferred name |

**Returns:** `str` — The original name if unique, otherwise `<name>.001`, `<name>.002`, etc.

---

#### find_by_data(id_data)

Find the object that uses a specific data block.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `id_data` | `bpy.types.ID` | — | The data block to search for (e.g., mesh, armature) |

**Returns:** `bpy.types.Object` or `None` — The object using that data block.

---

#### get_list_of_children(parent_object)

Get all direct children of an object.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `parent_object` | `bpy.types.Object` | — | The parent object |

**Returns:** `list[bpy.types.Object]` — List of child objects.

---

### Selection Filtering

#### get_selected_objects(exclude_non_mh_objects=False, exclude_mesh_objects=False, exclude_armature_objects=False, exclude_meta_objects=True)

Get selected objects with optional filtering.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `exclude_non_mh_objects` | `bool` | `False` | Exclude objects without an MPFB `object_type` |
| `exclude_mesh_objects` | `bool` | `False` | Exclude mesh objects |
| `exclude_armature_objects` | `bool` | `False` | Exclude armature objects |
| `exclude_meta_objects` | `bool` | `True` | Exclude objects that are neither mesh nor armature |

**Returns:** `list[bpy.types.Object]` — Filtered list of selected objects.

---

#### get_selected_armature_objects()

Get all selected armature objects.

**Returns:** `list[bpy.types.Object]` — List of selected armature objects.

---

#### get_selected_mesh_objects()

Get all selected mesh objects.

**Returns:** `list[bpy.types.Object]` — List of selected mesh objects.

---

### Object Type Identification

#### get_object_type(blender_object)

Get the MPFB object type of an object.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to query |

**Returns:** `str` — The object type (e.g., `"Basemesh"`, `"Skeleton"`) or empty string if not set.

---

#### object_is(blender_object, mpfb_type_name)

Check if an object matches one or more MPFB types.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to check |
| `mpfb_type_name` | `str` or `Sequence[str]` | — | Type name or list of acceptable type names |

**Returns:** `bool` — `True` if the object matches any of the specified types.

Type matching is case-insensitive and uses substring matching.

---

#### object_is_basemesh(blender_object)

Check if an object is a basemesh.

**Returns:** `bool` — `True` if `object_type == "Basemesh"`.

---

#### object_is_skeleton(blender_object)

Check if an object is a skeleton.

**Returns:** `bool` — `True` if `object_type == "Skeleton"`.

---

#### object_is_subrig(blender_object)

Check if an object is a subrig.

**Returns:** `bool` — `True` if `object_type == "Subrig"`.

---

#### object_is_any_skeleton(blender_object)

Check if an object is any skeleton type.

**Returns:** `bool` — `True` if `object_type` is `"Skeleton"` or `"Subrig"`.

---

#### object_is_body_proxy(blender_object)

Check if an object is a body proxy.

**Returns:** `bool` — `True` if `object_type` is `"Proxymesh"` or `"Proxymeshes"`.

---

#### object_is_eyes(blender_object)

Check if an object is eyes.

**Returns:** `bool` — `True` if `object_type == "Eyes"`.

---

#### object_is_basemesh_or_body_proxy(blender_object)

Check if an object is a basemesh or body proxy.

**Returns:** `bool` — `True` if the object is a basemesh or proxy.

---

#### object_is_any_mesh(blender_object)

Check if an object is a mesh (Blender type).

**Returns:** `bool` — `True` if the object exists and has type `MESH`.

---

#### object_is_any_makehuman_mesh(blender_object)

Check if an object is a mesh with an MPFB object type.

**Returns:** `bool` — `True` if it's a mesh with a valid `object_type`.

---

#### object_is_any_mesh_asset(blender_object)

Check if an object is a mesh asset (clothes, eyes, hair, etc.).

**Returns:** `bool` — `True` if the object is a mesh with a mesh asset type.

---

#### object_is_any_makehuman_object(blender_object)

Check if an object has any MPFB object type set.

**Returns:** `bool` — `True` if the object has a valid `object_type`.

---

### Relationship Queries

#### find_object_of_type_amongst_nearest_relatives(blender_object, mpfb_type_name="Basemesh", *, only_parents=False, strict_parent=False, only_children=False)

Find a single object of the specified type among relatives.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The starting object |
| `mpfb_type_name` | `str` or `Sequence[str]` | `"Basemesh"` | Type(s) to search for |
| `only_parents` | `bool` | `False` | Only search up the parent chain |
| `strict_parent` | `bool` | `False` | Stop at non-MakeHuman parents |
| `only_children` | `bool` | `False` | Only search children |

**Returns:** `bpy.types.Object` or `None` — The first matching object found.

Searches the object itself, its children, parents, and siblings.

---

#### find_all_objects_of_type_amongst_nearest_relatives(blender_object, mpfb_type_name="Basemesh", *, only_parents=False, strict_parent=False, only_children=False)

Find all objects of the specified type among relatives.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The starting object |
| `mpfb_type_name` | `str` or `Sequence[str]` | `"Basemesh"` | Type(s) to search for |
| `only_parents` | `bool` | `False` | Only search up the parent chain |
| `strict_parent` | `bool` | `False` | Stop at non-MakeHuman parents |
| `only_children` | `bool` | `False` | Only search children |

**Returns:** `Generator[bpy.types.Object]` — Generator yielding matching objects.

---

#### find_related_objects(blender_object, **kwargs)

Find all related MPFB objects.

**Returns:** `Generator[bpy.types.Object]` — Generator yielding all related MPFB objects.

---

#### find_related_skeletons(blender_object, **kwargs)

Find all related skeleton objects.

**Returns:** `Generator[bpy.types.Object]` — Generator yielding skeleton objects.

---

#### find_related_mesh_base_or_assets(blender_object, **kwargs)

Find all related mesh objects (basemesh and assets).

**Returns:** `Generator[bpy.types.Object]` — Generator yielding mesh objects.

---

#### find_related_mesh_assets(blender_object, **kwargs)

Find all related mesh asset objects (not basemesh).

**Returns:** `Generator[bpy.types.Object]` — Generator yielding mesh asset objects.

---

#### find_related_body_part_assets(blender_object, **kwargs)

Find all related body part assets (eyes, teeth, etc.).

**Returns:** `Generator[bpy.types.Object]` — Generator yielding body part objects.

---

#### find_deformed_child_meshes(armature_object)

Find all mesh objects deformed by an armature.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to check |

**Returns:** `Generator[bpy.types.Object]` — Generator yielding deformed mesh objects.

---

### Rigify Integration

#### object_is_generated_rigify_rig(blender_object)

Check if an object is a generated Rigify rig.

**Returns:** `bool` — `True` if the armature has a `rig_id` data property.

---

#### object_is_rigify_metarig(blender_object, *, check_bones=False)

Check if an object is a Rigify metarig.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to check |
| `check_bones` | `bool` | `False` | Also check bones for `rigify_type` property |

**Returns:** `bool` — `True` if the object is a Rigify metarig.

---

#### find_rigify_metarig_by_rig(blender_object)

Find the metarig associated with a generated Rigify rig.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The generated rig |

**Returns:** `bpy.types.Object` or `None` — The associated metarig.

---

#### find_rigify_rig_by_metarig(blender_object)

Find the generated rig associated with a Rigify metarig.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The metarig |

**Returns:** `bpy.types.Object` or `None` — The generated rig.

---

#### find_armature_context_objects(armature_object, *, operator=None, is_subrig=None, only_basemesh=False)

Find the base rig, basemesh, and directly controlled mesh for an armature.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature to analyze |
| `operator` | `bpy.types.Operator` | `None` | Operator for error reporting |
| `is_subrig` | `bool` | `None` | Override subrig detection |
| `only_basemesh` | `bool` | `False` | Only find basemesh, not direct mesh |

**Returns:** `tuple[Object, Object, Object]` — `(base_rig, basemesh, direct_mesh)`, any may be `None`.

---

### File Operations

#### load_wavefront_file(filepath, context=None)

Load a Wavefront OBJ file into Blender.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filepath` | `str` | — | Path to the OBJ file |
| `context` | `bpy.types.Context` | `None` | Blender context |

**Returns:** `bpy.types.Object` — The loaded mesh object.

**Raises:** `ValueError` if filepath is None, `IOError` if file doesn't exist.

---

#### save_wavefront_file(filepath, mesh_object, context=None)

Save a mesh object to a Wavefront OBJ file.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filepath` | `str` | — | Path for the OBJ file |
| `mesh_object` | `bpy.types.Object` | — | The mesh to save |
| `context` | `bpy.types.Context` | `None` | Blender context |

**Returns:** None

**Raises:** `ValueError` if filepath is None or mesh_object is invalid.

---

#### load_base_mesh(context=None, scale_factor=1.0, load_vertex_groups=True, exclude_vertex_groups=None)

Load the MPFB base mesh.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `context` | `bpy.types.Context` | `None` | Blender context |
| `scale_factor` | `float` | `1.0` | Scale to apply to the mesh |
| `load_vertex_groups` | `bool` | `True` | Whether to load vertex groups |
| `exclude_vertex_groups` | `list[str]` | `None` | Vertex groups to skip |

**Returns:** `bpy.types.Object` — The loaded basemesh with smooth shading and MPFB properties set.

---

### Vertex Group Operations

#### has_vertex_group(blender_object, vertex_group_name)

Check if an object has a specific vertex group.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to check |
| `vertex_group_name` | `str` | — | The vertex group name |

**Returns:** `bool` — `True` if the vertex group exists.

---

#### get_vertex_indexes_for_vertex_group(blender_object, vertex_group_name)

Get vertex indices belonging to a vertex group.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The mesh object |
| `vertex_group_name` | `str` | — | The vertex group name |

**Returns:** `list[int]` — List of vertex indices.

---

#### assign_vertex_groups(blender_object, vertex_group_definition, exclude_groups=None)

Assign vertex groups from a definition dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The mesh object |
| `vertex_group_definition` | `dict` | — | Dict mapping group names to vertex index lists |
| `exclude_groups` | `list[str]` | `None` | Groups to skip |

**Returns:** None

---

#### get_base_mesh_vertex_group_definition()

Get the standard vertex group definition for the base mesh.

**Returns:** `dict` — Dictionary mapping group names to lists of vertex indices.

Results are cached after first load.

---

### Mesh Utilities

#### get_lowest_point(basemesh, take_shape_keys_into_account=True)

Get the lowest Z coordinate of a basemesh.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The mesh object |
| `take_shape_keys_into_account` | `bool` | `True` | Consider shape key deformation |

**Returns:** `float` — The minimum Z coordinate.

Useful for positioning characters on a ground plane.

---

#### get_face_to_vertex_table()

Get the face-to-vertex mapping table for the base mesh.

**Returns:** `dict` — Dictionary mapping face indices to vertex index lists.

Results are cached after first load.

---

#### get_vertex_to_face_table()

Get the vertex-to-face mapping table for the base mesh.

**Returns:** `dict` — Dictionary mapping vertex indices to face index lists.

Results are cached after first load.

---

#### extract_vertex_group_to_new_object(existing_object, vertex_group_name)

Extract a vertex group into a new mesh object.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `existing_object` | `bpy.types.Object` | — | The source mesh |
| `vertex_group_name` | `str` | — | The vertex group to extract |

**Returns:** `bpy.types.Object` — A new mesh object containing only the extracted vertices.

---

## Examples

### Loading and Manipulating the Base Mesh

```python
from mpfb.services.objectservice import ObjectService
import bpy

# Load the base mesh at 10% scale
basemesh = ObjectService.load_base_mesh(
    context=bpy.context,
    scale_factor=0.1,
    load_vertex_groups=True
)

# Make it active
ObjectService.activate_blender_object(basemesh, deselect_all=True)

# Check what type it is
print(ObjectService.get_object_type(basemesh))  # "Basemesh"
```

### Finding Related Objects

```python
from mpfb.services.objectservice import ObjectService

# Starting from any object in a character hierarchy
selected = bpy.context.active_object

# Find the basemesh
basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(
    selected, "Basemesh"
)

# Find all clothes
for clothes in ObjectService.find_all_objects_of_type_amongst_nearest_relatives(
    basemesh, "Clothes", only_children=True
):
    print(f"Found clothes: {clothes.name}")

# Find the skeleton
skeleton = ObjectService.find_object_of_type_amongst_nearest_relatives(
    basemesh, "Skeleton"
)
```

### Working with Rigify

```python
from mpfb.services.objectservice import ObjectService

armature = bpy.context.active_object

if ObjectService.object_is_generated_rigify_rig(armature):
    # Find the metarig
    metarig = ObjectService.find_rigify_metarig_by_rig(armature)
    print(f"Metarig: {metarig.name}")
elif ObjectService.object_is_rigify_metarig(armature):
    # Find the generated rig
    rig = ObjectService.find_rigify_rig_by_metarig(armature)
    if rig:
        print(f"Generated rig: {rig.name}")
```

### Creating Custom Objects

```python
from mpfb.services.objectservice import ObjectService

# Create an empty as a parent
parent_empty = ObjectService.create_empty("CharacterRoot", empty_type="PLAIN_AXES")

# Create a mesh parented to it
mesh_obj = ObjectService.create_blender_object_with_mesh(
    name="CustomMesh",
    parent=parent_empty
)

# Create an armature parented to the empty
armature_obj = ObjectService.create_blender_object_with_armature(
    name="CustomRig",
    parent=parent_empty
)
```
