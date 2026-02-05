# ObjectService

ObjectService provides a comprehensive collection of static utility methods for managing and manipulating Blender objects. It handles creation, linking, selection, and removal of objects; finding and identifying objects by type and parent/child relationships; loading and saving meshes to OBJ files; and working with vertex groups.

## Source

`src/mpfb/services/objectservice.py`

## Dependencies

- `LogService` — logging
- `LocationService` — file path resolution
- `GeneralObjectProperties` — custom object property access
- `TargetService` — shape key operations (imported at call time)
- `MaterialService` — material deletion (imported at call time)

## Public API

### random_name()

Generate a random string of 15 lowercase ASCII characters.

### delete_object_by_name(name)

Safely delete an object by name, skipping gracefully if not found.

### delete_object(object_to_delete)

Safely delete an object, skipping if `None`.

### object_name_exists(name)

Check if an object with the given name exists in the scene.

### ensure_unique_name(desired_name)

Make a name unique by appending incrementing numbers if a name clash exists.

### activate_blender_object(object_to_make_active, *, context=None, deselect_all=False)

Make the given object selected and active, optionally deselecting all others first.

### select_object(obj)

Select an object and make it active (convenience alias).

### deselect_and_deactivate_all()

Ensure no object is selected or active.

### has_vertex_group(blender_object, vertex_group_name)

Check if the object has the specified vertex group.

### get_vertex_indexes_for_vertex_group(blender_object, vertex_group_name)

Get the indices of vertices belonging to the specified vertex group.

### create_blender_object_with_mesh(name="NewObject", parent=None, skip_linking=False)

Create a new mesh object with an empty mesh data block.

### create_blender_object_with_armature(name="NewObject", parent=None)

Create a new armature object with an armature data block.

### create_empty(name, empty_type="SPHERE", parent=None)

Create a new empty object with the specified draw type and optional parent.

### link_blender_object(object_to_link, collection=None, parent=None)

Link an object to a collection and optionally assign a parent.

### get_list_of_children(parent_object)

Return a list of objects whose parent is set to the given object.

### find_by_data(id_data)

Find the Blender object that uses the specified data block.

### get_selected_objects(exclude_non_mh_objects=False, exclude_mesh_objects=False, exclude_armature_objects=False, exclude_meta_objects=True)

Find selected objects with optional exclusion filters.

### get_selected_armature_objects()

Find all selected armature objects.

### get_selected_mesh_objects()

Find all selected mesh objects.

### get_object_type(blender_object)

Return the `object_type` custom property value of the object.

### object_is(blender_object, mpfb_type_name)

Check if the object matches the given MPFB type name(s).

### object_is_basemesh(blender_object)

Check if the object has `object_type == "Basemesh"`.

### object_is_skeleton(blender_object)

Check if the object is of type `"Skeleton"`.

### object_is_subrig(blender_object)

Check if the object is of type `"Subrig"`.

### object_is_any_skeleton(blender_object)

Check if the object is of any skeleton type.

### object_is_body_proxy(blender_object)

Check if the object has a `Proxymesh` or `Proxymeshes` type.

### object_is_eyes(blender_object)

Check if the object has `object_type == "Eyes"`.

### object_is_basemesh_or_body_proxy(blender_object)

Check if the object is a Basemesh or Proxymesh type.

### object_is_any_mesh(blender_object)

Check if the object is not `None` and has Blender type `MESH`.

### object_is_any_makehuman_mesh(blender_object)

Check if the object is a `MESH` with a valid MPFB `object_type`.

### object_is_any_mesh_asset(blender_object)

Check if the object is a `MESH` with a mesh asset `object_type`.

### object_is_any_makehuman_object(blender_object)

Check if the object has a valid MPFB `object_type`.

### find_object_of_type_amongst_nearest_relatives(blender_object, mpfb_type_name="Basemesh", *, only_parents=False, strict_parent=False, only_children=False)

Find one object of the given type among children, parents, and siblings.

### find_all_objects_of_type_amongst_nearest_relatives(blender_object, mpfb_type_name="Basemesh", *, only_parents=False, strict_parent=False, only_children=False)

Find all objects of the given type among nearest relatives (generator).

### find_related_objects(blender_object, **kwargs)

Find related objects of any MPFB type among nearest relatives.

### find_related_skeletons(blender_object, **kwargs)

Find related skeleton objects among nearest relatives.

### find_related_mesh_base_or_assets(blender_object, **kwargs)

Find related mesh base or asset objects among nearest relatives.

### find_related_mesh_assets(blender_object, **kwargs)

Find related mesh asset objects among nearest relatives.

### find_related_body_part_assets(blender_object, **kwargs)

Find related body part asset objects among nearest relatives.

### find_deformed_child_meshes(armature_object)

Find all mesh objects deformed by the given armature object.

### object_is_generated_rigify_rig(blender_object)

Check if the object is a generated Rigify rig.

### object_is_rigify_metarig(blender_object, *, check_bones=False)

Check if the object is a Rigify metarig.

### find_rigify_metarig_by_rig(blender_object)

Find the Rigify metarig associated with a given Rigify rig.

### find_rigify_rig_by_metarig(blender_object)

Find the Rigify rig associated with a given Rigify metarig.

### find_armature_context_objects(armature_object, *, operator=None, is_subrig=None, only_basemesh=False)

Find the base rig, basemesh, and directly controlled meshes for an armature.

### load_wavefront_file(filepath, context=None)

Load a Wavefront (.obj) file into Blender.

### save_wavefront_file(filepath, mesh_object, context=None)

Save a Blender mesh object to a Wavefront (.obj) file.

### load_base_mesh(context=None, scale_factor=1.0, load_vertex_groups=True, exclude_vertex_groups=None)

Load the MPFB base mesh from its OBJ file and apply transformations.

### assign_vertex_groups(blender_object, vertex_group_definition, exclude_groups=None)

Assign vertex groups to an object based on a group definition dictionary.

### get_base_mesh_vertex_group_definition()

Get the vertex group definition for the base mesh.

### get_lowest_point(basemesh, take_shape_keys_into_account=True)

Get the lowest Z-coordinate of the base mesh.

### get_face_to_vertex_table()

Get the face-to-vertex mapping table for the base mesh.

### get_vertex_to_face_table()

Get the vertex-to-face mapping table for the base mesh.

### extract_vertex_group_to_new_object(existing_object, vertex_group_name)

Extract the vertices of a vertex group into a new mesh object.

## Example

```python
from mpfb.services.objectservice import ObjectService

basemesh = ObjectService.load_base_mesh(context=bpy.context, scale_factor=0.1)
ObjectService.activate_blender_object(basemesh, deselect_all=True)
children = ObjectService.get_list_of_children(basemesh)
```
