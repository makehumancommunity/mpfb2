# SocketObject entities

## Overview

The `socketobject` package holds the staging objects for importing a character from a running MakeHuman instance. [SocketService](../services/socketservice.md) does the talking; these three classes hold what comes back and turn it into blender objects.

The design is numpy-first and deliberately so. MakeHuman sends geometry as raw binary buffers, one call per array, together with a `SocketMeshInfo` dict saying what shape and element type each buffer has. Each class reshapes those buffers into numpy arrays, does all the sorting, swapping and grouping while the data is still numpy, and only then hands finished lists to blender. Converting earlier, vertex by vertex, is an order of magnitude slower.

There are three classes in one hierarchy:

| Class | Module | Role |
|-------|--------|------|
| `SocketMeshObject` | `socketmeshobject.py` | Abstract base. Owns the numpy arrays, the vertex group bookkeeping and everything which is common to any mesh arriving over the socket. Not meant to be instanced directly. |
| `SocketBodyObject` | `socketbodyobject.py` | The base mesh, that is the human itself. Adds helper geometry and joint cube vertex groups, the ground joint measurement and the optional skeleton. |
| `SocketProxyObject` | `socketproxyobject.py` | Everything else: clothes, eyes, hair, a body proxy and so on. One instance per proxy. |

Both concrete classes do their work **in the constructor**. Constructing one issues the socket calls, fetches the buffers and arranges every array, so an instance which exists at all is fully populated; `as_blender_mesh_object()` is then a separate step which creates the blender object. That is why the numpy arrays are typed `numpy.ndarray | None` — they are `None` only between the base constructor and the `arrange_*` calls the subclass constructor makes immediately afterwards.

The `importer_presets` dict both classes are constructed with is the one `IMPORTER_PRESETS_PROPERTIES.as_dict()` builds in the UI layer. It is read directly, key by key, and the keys read are `scale_factor`, `extra_vertex_groups`, `import_rig`, `import_body`, `prefix_object_names`, `handle_helpers`, `detailed_helpers`, `add_subdiv_modifier`, `subdiv_levels` and `rig_as_parent`. Although the argument defaults to `None`, **`None` is not a supported value**: both constructors subscript the dict unconditionally while still running, so passing it, or omitting the argument, raises `TypeError`.

## Source

- `src/mpfb/entities/socketobject/__init__.py`
- `src/mpfb/entities/socketobject/_extra_vertex_groups.py`
- `src/mpfb/entities/socketobject/socketmeshobject.py`
- `src/mpfb/entities/socketobject/socketbodyobject.py`
- `src/mpfb/entities/socketobject/socketproxyobject.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging, one logger per module |
| `SocketService` | Every socket call, both the JSON metadata and the binary geometry |
| `ObjectService` | `create_blender_object_with_mesh()` and `link_blender_object()` |
| `ModifierService` | `create_armature_modifier()` when a rig is the parent |
| `RigService` | `create_rig_from_skeleton_info()`, body object only |
| `GeneralObjectProperties` | Stamping `object_type` and `scale_factor` on the created objects |
| `mpfb.types` | `SocketMeshInfo`, `SocketWeightInfo` and `SocketSkeletonInfo` |
| `numpy` | All array work |

## Module-Level Data

| Name | Type | Description |
|------|------|-------------|
| `ALL_EXTRA_GROUPS` | `dict[str, dict[str, list[int]]]` | Copy of `vertex_group_information`: the extra vertex groups MPFB adds which MakeHuman itself does not send, keyed by `"basemesh"` for the base mesh and by a proxy's uuid for a proxy. Read by `HumanService` and the asset library operators as well as from here. |
| `BASEMESH_EXTRA_GROUPS` | `dict[str, list[int]]` | Copy of the `"basemesh"` entry of the same dict, that is group name to vertex indices. Read by `ObjectService` and `HumanService`. |
| `vertex_group_information` | `dict[str, dict[str, list[int]]]` | The underlying table, in the private `_extra_vertex_groups.py`. It is a generated file of literal index lists and is the single source for both constants above. |
| `groups_which_should_not_get_specific_material` | `list[str]` | Declared beside it, and currently read nowhere in the tree. |

## SocketMeshObject

The abstract base. Its own `__init__` only sets up empty state; everything else is called by a subclass constructor, in the order the subclass chooses.

### Attributes

Prefixed with an underscore and not part of a public contract, but worth knowing when reading a subclass.

| Attribute | Type | Description |
|-----------|------|-------------|
| `_importer_presets` | `dict[str, Any]` | The presets dict the caller passed. See the note on `None` in the Overview. |
| `_object_info` | `SocketMeshInfo` | The metadata dict for this mesh. Empty until a subclass assigns one. |
| `_object_type` | `str` | `"Basemesh"` for the body, the proxy's own `type` for a proxy, `"GENERAL"` by default. |
| `_vertices` | `numpy.ndarray \| None` | Shape `[vertex count, 3]`, in blender coordinates and already rescaled. |
| `_faces` | `numpy.ndarray \| None` | Shape `[face count, columns per face]`, holding vertex indices. |
| `_texco` | `numpy.ndarray \| None` | The texture coordinates, shape `[count, 2]`. |
| `_uvmappings` | `numpy.ndarray \| None` | Per face indices into `_texco`. |
| `_sorted_face_uv_and_texco` | `numpy.ndarray \| None` | `_texco` picked through `_uvmappings`, that is the UV coordinates already in face order, ready for `foreach_set`. |
| `_vertex_groups_by_name` | `dict[str, numpy.ndarray]` | Group name to the vertex indices in it. This is the accumulator every `arrange_*` method writes into. |
| `_vertex_groups_by_index` | `dict[Any, Any]` | Never populated or read; only deleted in `__del__`. |
| `_weight_info` | `SocketWeightInfo \| None` | The weight index, which a subclass must set before calling `arrange_weights()`. |
| `_weights_by_name` | `dict[str, numpy.ndarray]` | Bone name to the weight values for the vertices in the group of the same name. Parallel to `_vertex_groups_by_name`. |
| `_scale` | `float` | The factor `arrange_vertices()` applied, and what gets stamped on the blender object as `scale_factor`. `1` for decimeters. |

### Public API

#### `__init__(importer_presets=None, object_type="GENERAL")`

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `importer_presets` | `dict[str, Any] \| None` | `None` | The importer presets. The default is not usable, see the Overview. |
| `object_type` | `str` | `"GENERAL"` | The object type a subclass wants stamped on the result |

**Returns:** `None`.

---

#### `__del__()`

Deletes the four largest attributes and calls `gc.collect()`, to help garbage collection along after an import. Its own docstring is candid that it is unclear whether this helps.

**Returns:** `None`.

---

#### `get_importer_presets()`

**Returns:** `dict[str, Any]` — the presets dict handed to the constructor.

---

#### `get_object_info()`

**Returns:** `SocketMeshInfo` — the metadata dict for this mesh. See [SocketService](../services/socketservice.md) for the shape.

---

#### `get_object_type()`

**Returns:** `str` — `"Basemesh"`, or the proxy type such as `"Clothes"`, `"Proxymeshes"` or `"Eyes"`.

---

#### `get_name()`

**Returns:** `str` — the `name` entry of the object info. Raises `KeyError` if the info does not carry one, where `as_blender_mesh_object()` in both subclasses reads the same entry with a fallback.

---

#### `get_filename()`

**Returns:** `str` — the `filename` entry of the object info. Only the base mesh info carries one; for a proxy this raises `KeyError`.

---

#### `convert_to_shaped_numpy_array(shape_key, type_code_key, data_from_socket, rescale=None)`

Turn one raw binary payload into a correctly shaped numpy array. This is the workhorse behind all four `arrange_*` methods which read geometry.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `shape_key` | `str` | — | Which entry of the object info holds the shape, for example `"verticesShape"` |
| `type_code_key` | `str` | — | Which entry holds the numpy type code, for example `"verticesTypeCode"` |
| `data_from_socket` | `bytearray` | — | The raw payload, as returned by one of `SocketService`'s binary calls |
| `rescale` | `float \| None` | `None` | A factor applied to every value in the array. `None` means no rescaling, which is not the same as `1` only in that the multiplication is skipped. |

**Returns:** `numpy.ndarray` — the reshaped, optionally rescaled array.

---

#### `arrange_vertices(data_from_socket)`

Read the vertex buffer into `_vertices`, applying both the scale from the presets and the coordinate system conversion.

The conversion is in two steps, because MakeHuman and blender disagree twice: MakeHuman sends vertices in XZY order, so columns 1 and 2 are swapped, and MakeHuman's Y is blender's negative Y, so the new column 1 is then multiplied by `-1`.

The scale comes from the presets' `scale_factor`: `"DECIMETER"` leaves the data alone, `"METER"` multiplies by `0.1` and `"CENTIMETER"` by `10.0`. Any other value is treated as decimeters. Whatever is applied is also recorded in `_scale`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `data_from_socket` | `bytearray` | — | The vertex payload |

**Returns:** `None`.

---

#### `arrange_faces(data_from_socket)`

Read the face buffer into `_faces`. No conversion is needed; these are vertex indices.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `data_from_socket` | `bytearray` | — | The face payload |

**Returns:** `None`.

---

#### `arrange_uv_and_texco(uv_data_from_socket, texco_data_from_socket)`

Read both UV buffers, then combine them: `_sorted_face_uv_and_texco` is `_texco` indexed by `_uvmappings`, which puts the coordinates in the order `create_uv_layer()` needs to hand them straight to `foreach_set`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `uv_data_from_socket` | `bytearray` | — | The face-to-UV mapping payload |
| `texco_data_from_socket` | `bytearray` | — | The texture coordinate payload |

**Returns:** `None`.

---

#### `arrange_weights(weights_vertices_data, weights_data)`

Slice the two parallel weight payloads into per bone arrays, writing the vertex indices into `_vertex_groups_by_name` and the weight values into `_weights_by_name` under the same key.

The slicing is driven entirely by `_weight_info`: the order of its `weights` list and each entry's `numVertices` are what say where one bone's run of values ends and the next begins. A subclass must therefore have assigned `_weight_info` before calling this.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `weights_vertices_data` | `bytearray` | — | The vertex index payload, read as `int32` |
| `weights_data` | `bytearray` | — | The weight value payload, read as `float32` |

**Returns:** `None`.

**Raises:** `ValueError` if `_weight_info` is `None` or empty.

---

#### `arrange_face_group_arrays()`

Convert MakeHuman's *face* groups into blender *vertex* groups. A face group is a name plus a list of start/stop face ranges, so for each range the faces are sliced out of `_faces`, flattened and deduplicated into a list of vertex indices.

Returns without doing anything if the object info carries no `faceGroups`.

Note that only a group's **first** range reaches `_vertex_groups_by_name`. The branch which handles a second or later range computes the concatenation but does not store it, so a face group split over more than one range contributes only the vertices of its first.

**Returns:** `None`.

---

#### `create_vertex_groups_from_dict(group_information)`

Add vertex groups from a literal mapping of group name to vertex indices, which is how the extra groups in `_extra_vertex_groups.py` are applied. Entries overwrite any group of the same name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `group_information` | `dict[str, list[int]]` | — | Group name to the vertex indices to put in it |

**Returns:** `None`.

---

#### `arrange_face_mask_array(mask_applicable_to_group=None)`

Build the `"Delete"` vertex group from the face mask. The face mask is the inverted sum of all delete groups, and arrives as a list of start/stop ranges of faces to **display**; what blender needs is a group of vertices to **hide**, so this inverts it.

Returns without doing anything if the object info carries no `faceMask`, or if the mask is zero length.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mask_applicable_to_group` | `str \| None` | `None` | Limit the candidate vertices to this existing group. `None` considers every vertex a candidate. |

**Returns:** `None`.

Two things are worth knowing about the `None` case, which is the one proxies use. The candidate set is built from `_vertices.size`, which for a two-dimensional array is the number of *values* rather than the number of vertices, so it runs to three times the vertex count. The surplus indices do not name vertices: blender silently ignores them when the group is built, so the group which reaches the mesh is correct, but the array held here is not, and it is never empty — which is why a proxy whose mask covers every face still gets a `"Hide delete group"` modifier. That modifier inverts the group, so an empty one hides nothing and the result still looks right.

---

#### `apply_vertex_weights_if_needed(mesh, vertex_group)`

Write the real weight values into an existing blender vertex group.

The group is expected to have been created already with all its vertices added at weight `1.0`; this walks the two parallel arrays from `arrange_weights()` and updates each vertex's weight in place. Adding all vertices in one call and then updating is substantially faster than adding each vertex with its weight individually.

Logs a warning and returns if the group is not in `_vertex_groups_by_name`; logs at debug level and returns if there are simply no weights for it, which is the normal case for a face group.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh` | `bpy.types.Mesh` | — | The mesh data block holding the vertices |
| `vertex_group` | `bpy.types.VertexGroup` | — | The group to update. Its `name` is what is looked up. |

**Returns:** `None`.

---

#### `create_uv_layer(mesh)`

Create a new UV layer on the mesh and fill it from `_sorted_face_uv_and_texco` in a single `foreach_set` call.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh` | `bpy.types.Mesh` | — | The mesh data block to add the layer to |

**Returns:** `None`.

---

## SocketBodyObject

The base mesh. Subclasses `SocketMeshObject` with `object_type="Basemesh"`.

### Public API

#### `__init__(importer_presets=None)`

Fetch and arrange the entire base mesh. In order: the mesh info, the vertices, the faces, the UV data, the face groups, the extra vertex groups if the presets ask for them, the face mask limited to the `"body"` group, and the helper face groups. Then, if the presets ask for a rig, the skeleton info and — if that skeleton is real — the weights.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `importer_presets` | `dict[str, Any] \| None` | `None` | The importer presets. The default is not usable, see the Overview. |

**Returns:** `None`.

**Raises:** `TypeError` if MakeHuman answers the mesh info call without data. The reply is subscripted on the next line, so a call which failed for any reason surfaces here rather than as a reported error.

---

#### `has_rig()`

**Returns:** `bool` — whether a real skeleton was found. False until `arrange_skeleton_info()` has run, and false afterwards if the skeleton is named `"none"` or has no bones.

---

#### `get_ground_joint_mean()`

The Z coordinate of the centre of the `joint-ground` joint cube, which is what the importer uses to put the character's feet on the ground.

**Returns:** `float` — the mean of the Z column of the joint cube's vertices.

**Raises:** `KeyError` if the `joint-ground` group is absent, which it is when the presets exclude joint cubes.

---

#### `arrange_extra_vertex_groups()`

Add the base mesh's extra vertex groups from `_extra_vertex_groups.py`.

**Returns:** `None`.

---

#### `arrange_helper_face_group_arrays()`

Build two summary groups from the groups already collected: `"HelperGeometry"`, the concatenation of every group whose name starts with `helper-`, and `"JointCubes"`, the concatenation of every group whose name starts with `joint-`.

**Returns:** `None`.

**Raises:** `ValueError` from `numpy.concatenate` if there is nothing to concatenate, which is the case when the face groups have not been arranged first.

---

#### `arrange_skeleton_info()`

Fetch the skeleton from MakeHuman and decide whether it is real, which it is when its name is not `"none"` and it has at least one bone.

**Returns:** `None`.

**Raises:** `TypeError` if MakeHuman answers without data, for the same reason as the constructor.

---

#### `as_blender_mesh_object(collection=None)`

Create the blender objects. Which objects, and how they relate, is decided by the presets:

- `import_body` creates the mesh object, stamped with `object_type` `"Basemesh"` and the scale factor that was applied.
- `import_rig`, together with a real skeleton, creates the armature from the skeleton info, stamped with `object_type` `"Skeleton"`.
- `prefix_object_names` decides whether the mesh is named `<character>.body` or just `body`, and only applies when there is a rig.
- `rig_as_parent` decides whether the armature is used as the mesh's parent.

If both objects exist and the parent really is an armature, an armature modifier is added to the mesh.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `collection` | `bpy.types.Collection \| None` | `None` | The collection to link the mesh into. `None` links into the active collection. |

**Returns:** `tuple[bpy.types.Object \| None, bpy.types.Object \| None]` — the mesh and the armature, in that order. Either or both is `None`, depending on the presets.

---

### Private helpers

#### `_create_mesh_object(mesh_name)`

Creates the mesh data block from the numpy arrays with `from_pydata`, marks every polygon smooth, creates each vertex group and weights it, adds the UV layer, and finally adds the mask and subdivision modifiers the presets call for.

Two presets decide which vertex groups are created at all: with `handle_helpers` set to `"DELETE"` only the `"body"` group is wanted, since the helper geometry is being removed rather than masked, and with `detailed_helpers` off the individual `helper-` and `joint-` groups are skipped. The second test overwrites the first rather than adding to it, so with helpers being deleted and detailed helpers off, groups other than `"body"` are created after all. The surrounding block carries the maintainer's own `TODO` saying the helper deletion path is buggy and needs review.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_name` | `str` | — | Name for the new object and its mesh |

**Returns:** `bpy.types.Object` — the unlinked mesh object.

---

## SocketProxyObject

One proxy: clothes, a body proxy, eyes, hair and so on. Subclasses `SocketMeshObject` with the proxy's own `type` as the object type.

### Public API

#### `__init__(proxy_info, importer_presets=None, import_weights=False)`

Fetch and arrange one proxy. The proxy info is taken as given rather than fetched, since the importer already has it from `SocketService.get_proxies_info()`.

MakeHuman does not reliably send the four `*Shape` entries for a proxy, so the constructor fills in any that are missing from the matching count: `verticesShape` from `numVertices` as `[n, 3]`, `facesShape` from `numFaces` as `[n, 4]`, `textureCoordsShape` from `numTextureCoords` as `[n, 2]` and `faceUVMappingsShape` from `numFaceUVMappings` as `[n, 4]`. The code describes that as a workaround for a probable bug on the MakeHuman side.

It then arranges the vertices, faces, UV data, face groups, the face mask and the extra vertex groups, and fetches the weights if asked to.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `proxy_info` | `SocketMeshInfo` | — | One entry of `SocketService.get_proxies_info()`. Copied, not retained, since the copy is extended with the shapes above. |
| `importer_presets` | `dict[str, Any] \| None` | `None` | The importer presets. The default is not usable, see the Overview. |
| `import_weights` | `bool` | `False` | Whether to fetch and arrange this proxy's vertex weights |

**Returns:** `None`.

---

#### `get_lowest_point()`

**Returns:** `float` — the lowest Z coordinate of any vertex. The importer uses this together with the body's ground joint to decide how far to lift the whole character.

---

#### `arrange_extra_vertex_groups()`

Add this proxy's extra vertex groups, looked up by uuid in `_extra_vertex_groups.py`. Returns without doing anything if the proxy has no uuid, or if there are no extra groups recorded for it, which is the common case.

**Returns:** `None`.

---

#### `as_blender_mesh_object(parent=None, name_prefix=None)`

Create the blender object for this proxy: the mesh from the numpy arrays, every collected vertex group weighted, the UV layer, the subdivision modifier if the presets ask for one, an armature modifier if the parent is an armature, and the inverted delete mask if there is anything to hide. The object is stamped with the proxy's `type` as its `object_type` and with the scale factor that was applied, and is linked into the active collection.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `parent` | `bpy.types.Object \| None` | `None` | The object to parent to, normally the armature |
| `name_prefix` | `str \| None` | `None` | Prepended to the proxy name, separated by a dot. Anything after the first dot in the prefix is dropped, so `"Alice."` and `"Alice"` give the same result. |

**Returns:** `bpy.types.Object` — the linked proxy object.

---

## Examples

### Importing the base mesh

```python
from mpfb.entities.socketobject.socketbodyobject import SocketBodyObject

# In the addon this dict comes from IMPORTER_PRESETS_PROPERTIES.as_dict(). It is not optional:
# every key read below has to be present.
presets = {
    "scale_factor": "DECIMETER",
    "extra_vertex_groups": True,
    "import_rig": True,
    "import_body": True,
    "prefix_object_names": True,
    "handle_helpers": "MASK",
    "detailed_helpers": True,
    "add_subdiv_modifier": False,
    "subdiv_levels": 1,
    "rig_as_parent": True,
}

# Constructing it performs the whole import, so this is where the socket traffic happens
body = SocketBodyObject(presets)

print("Imported", body.get_name(), "with rig:", body.has_rig())
print("Ground joint at z =", body.get_ground_joint_mean())

basemesh, armature = body.as_blender_mesh_object()
```

### Importing the proxies

```python
from mpfb.services import SocketService
from mpfb.entities.socketobject.socketproxyobject import SocketProxyObject

for proxy_info in SocketService.get_proxies_info() or []:
    # Weights are only worth fetching when there is a rig to weight against
    proxy = SocketProxyObject(proxy_info, presets, import_weights=body.has_rig())
    print(proxy.get_object_type(), proxy_info["name"], "lowest point", proxy.get_lowest_point())
    proxy.as_blender_mesh_object(armature, name_prefix=body.get_name())
```

### Reading the extra vertex groups without importing anything

```python
from mpfb.entities.socketobject import ALL_EXTRA_GROUPS, BASEMESH_EXTRA_GROUPS

print("Extra base mesh groups:", sorted(BASEMESH_EXTRA_GROUPS.keys()))

# Keyed by uuid for a proxy, and most proxies have no entry at all
uuid = "some-proxy-uuid"
if uuid in ALL_EXTRA_GROUPS:
    for group_name, indices in ALL_EXTRA_GROUPS[uuid].items():
        print(group_name, "has", len(indices), "vertices")
```
