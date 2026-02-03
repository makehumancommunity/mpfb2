# MaterialService

MaterialService handles operations related to MPFB materials in Blender. It provides tools for creating, modifying, identifying, and managing materials assigned to Blender objects, including support for multiple material types (makeskin, enhanced skin, layered skin, game engine, procedural eyes) and ink layer management.

## Source

`src/mpfb/services/materialservice.py`

## Dependencies

- `LogService` — logging
- `LocationService` — path resolution
- `ObjectService` — Blender object operations
- `NodeService` — shader node manipulation
- `MeshService` — mesh operations

## Public API

### delete_all_materials(blender_object, also_destroy_groups=False)

Delete all materials from a Blender object, optionally destroying node groups.

### has_materials(blender_object)

Check if the object has any materials assigned.

### get_material(blender_object, slot=0)

Return the material in the given slot index.

### identify_material(material)

Determine the type of a material (returns strings like `"enhanced_skin"`, `"procedural_eyes"`, `"makeskin"`, etc.).

### set_normalmap(material, filename)

Modify a material to use the specified normal map file.

### assign_new_or_existing_material(name, blender_object)

Assign a material by name to an object, creating it if it does not already exist.

### create_empty_material(name, blender_object=None)

Create a new empty material, optionally assigning it to an object.

### create_v2_skin_material(name, blender_object=None, mhmat_file=None)

Create a v2 skin material, optionally from an `.mhmat` file.

### as_blend_path(path)

Convert a relative asset path to blend file information.

### save_material_in_blend_file(blender_object, path_to_blend_file, material_number=None, fake_user=False)

Save materials from an object to a `.blend` file.

### load_material_from_blend_file(path, blender_object=None)

Load a material from a `.blend` file, optionally assigning it to an object.

### create_and_assign_material_slots(basemesh, bodyproxy=None)

Create and assign material slots for body vertex groups on the basemesh.

### find_color_adjustment(blender_object)

Return all color adjustments currently applied to the object's material slots.

### apply_color_adjustment(blender_object, color_adjustment)

Apply color adjustments to the object's material slots.

### add_focus_nodes(material, uv_map_name=None)

Add the node setup required for ink layer focus.

### get_number_of_ink_layers(material)

Return the count of ink layers in a material.

### get_ink_layer_info(mesh_object, ink_layer=1)

Return UV map and texture info for a specific ink layer.

### load_ink_layer(mesh_object, ink_layer_json_path)

Load an ink layer from a JSON file onto a mesh object.

### remove_all_makeup(material, basemesh=None)

Remove all ink layers from a material.

### get_skin_diffuse_color()

Return the static skin material color for viewport display.

### get_generic_bodypart_diffuse_color()

Return the static body part material color.

### get_generic_clothes_diffuse_color()

Return the static clothes material color.

### get_eye_diffuse_color()

Return the static eye material color.

### get_teeth_diffuse_color()

Return the static teeth material color.

### get_diffuse_colors()

Return all static material colors as a dict.

## Example

```python
from mpfb.services.materialservice import MaterialService

MaterialService.create_and_assign_material_slots(basemesh)
mat_type = MaterialService.identify_material(basemesh.data.materials[0])
MaterialService.set_normalmap(basemesh.data.materials[0], "/path/to/normal.png")
```
