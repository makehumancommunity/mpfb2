# MaterialService

## Overview

MaterialService handles the creation, identification, modification, and management of materials assigned to Blender objects within MPFB. It supports multiple material types, each with distinct node tree structures: **MakeSkin** (the standard MakeHuman material format), **enhanced skin** (procedural skin with pore detail), **layered skin** (procedural skin with color control groups), **procedural eyes**, and **game engine** (simple Principled BSDF).

The service provides a complete material lifecycle: creating empty or skin-specific materials, assigning them to objects, creating per-body-part material slots, and loading/saving materials from `.blend` files. It also manages **ink layers** — stacked texture overlays used for makeup, tattoos, and other surface decorations — with support for adding, querying, and removing layers from both MakeSkin and layered skin materials.

MaterialService also provides static viewport diffuse colors for different body parts and a color adjustment system that can read and apply tint modifications to materials. All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/materialservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.materialservice")` |
| `LocationService` | Resolving paths to UV layer data and asset directories |
| `ObjectService` | Object activation, vertex group queries, material slot assignment |
| `NodeService` | Shader node creation, linking, querying, and manipulation |
| `MeshService` | Adding UV maps from dictionaries (for ink layer focus) |
| `NodeWrapperSkin` | Creating the v2 enhanced skin node group |
| `NodeWrapperMpfbAlphaMixer` | Creating alpha mixer nodes for ink layer blending |
| `MakeSkinMaterial` | Parsing `.mhmat` files for texture references (imported at call time) |

## Material Type Identifiers

The `identify_material()` method returns one of these string identifiers:

| Type | Description |
|------|-------------|
| `"empty"` | Material is `None` or has no nodes |
| `"enhanced_skin"` | Procedural skin with `Pore detail` parameter in a shader group |
| `"procedural_eyes"` | Procedural eyes with `IrisSection4Color` parameter in a shader group |
| `"layered_skin"` | Procedural skin with `NavelCenterOverride` parameter in a shader group |
| `"makeskin"` | MakeHuman MakeSkin material (has `diffuseIntensity` node) |
| `"gameengine"` | Simple material with a `Principled BSDF` node |
| `"unknown"` | None of the above patterns matched |

## Public API

### Material Lifecycle

#### create_empty_material(name, blender_object=None)

Create a new empty material with nodes enabled and `HASHED` blend method. Optionally assign it to a Blender object.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The name for the new material |
| `blender_object` | `bpy.types.Object` | `None` | Optional object to assign the material to |

**Returns:** `bpy.types.Material` — The newly created material.

---

#### assign_new_or_existing_material(name, blender_object)

Assign a material to an object by name. If a material with the given name already exists in `bpy.data.materials`, it is reused; otherwise, a new empty material is created.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The name of the material to assign |
| `blender_object` | `bpy.types.Object` | — | The object to assign the material to |

**Returns:** `bpy.types.Material` — The assigned material.

---

#### create_v2_skin_material(name, blender_object=None, mhmat_file=None)

Create a v2 enhanced skin material using the `NodeWrapperSkin` node group. Deletes any existing materials on the object first. If an `.mhmat` file is provided, diffuse and normal map textures are extracted and connected.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The name for the skin material |
| `blender_object` | `bpy.types.Object` | `None` | The object to assign the material to (required) |
| `mhmat_file` | `str` | `None` | Optional path to an `.mhmat` file for texture setup |

**Returns:** `bpy.types.Material` — The created skin material.

**Raises:** `ValueError` if `blender_object` is `None` or if the node tree cannot be determined.

---

#### delete_all_materials(blender_object, also_destroy_groups=False)

Delete all materials from a Blender object. Materials are renamed with an `.unused` suffix before removal. Optionally clears node groups as well. Orphaned material data blocks (zero users) are also removed.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to remove materials from |
| `also_destroy_groups` | `bool` | `False` | If `True`, also destroy node groups within each material |

**Returns:** None

---

#### create_and_assign_material_slots(basemesh, bodyproxy=None)

Create per-body-part material slots for the basemesh (and optionally a body proxy). Copies the base material and assigns instances to vertex groups: `nipple`, `lips`, `fingernails`, `toenails`, `ears`, and `genitals`. The basemesh must already have at least one material assigned.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The base mesh to create material slots on |
| `bodyproxy` | `bpy.types.Object` | `None` | Optional body proxy to also assign slots to |

**Returns:** None

**Raises:** `ValueError` if the basemesh has no initial material.

---

### Material Identification and Queries

#### has_materials(blender_object)

Check if a Blender object has any materials assigned in its material slots.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to check |

**Returns:** `bool` — `True` if the object has at least one material slot.

---

#### get_material(blender_object, slot=0)

Return the material in the specified material slot.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to query |
| `slot` | `int` | `0` | The material slot index |

**Returns:** `bpy.types.Material` or `None` — The material in the slot, or `None` if no materials exist.

---

#### identify_material(material)

Determine the type of a material by examining its node tree structure. Checks for characteristic nodes and parameters to classify the material.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `material` | `bpy.types.Material` | — | The material to identify |

**Returns:** `str` — One of the material type identifiers (see Constants section).

---

### Material Modification

#### set_normalmap(material, filename)

Set a normal map texture on a material. Creates the necessary normal map and image texture nodes if they don't exist, and connects them to the Principled BSDF or bump node. Works with `enhanced_skin`, `makeskin`, and `layered_skin` material types.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `material` | `bpy.types.Material` | — | The material to modify |
| `filename` | `str` | — | Absolute path to the normal map image file |

**Returns:** None

**Raises:** `ValueError` if the material type doesn't support normal maps.

---

#### find_color_adjustment(blender_object)

Return all color adjustments currently applied to the object's first material slot. Finds the mix node connected to the Principled BSDF's Base Color input and returns its socket values.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to query |

**Returns:** `dict` or `None` — Dictionary of socket values from the color adjustment node, or `None` if not found.

---

#### apply_color_adjustment(blender_object, color_adjustment)

Apply color adjustments to the object's first material slot. Sets the default values of the mix node connected to the Principled BSDF's Base Color input.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to modify |
| `color_adjustment` | `dict` | — | Dictionary of socket values to apply |

**Returns:** None

---

### Ink Layer Management

#### add_focus_nodes(material, uv_map_name=None)

Add a new ink layer to a material by creating the necessary node setup (alpha mixer, image texture, and UV map nodes). Supports both MakeSkin and layered skin materials. Handles first-layer and subsequent-layer creation differently, stacking layers through alpha mixer chains.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `material` | `bpy.types.Material` | — | The material to add ink layer nodes to |
| `uv_map_name` | `str` | `None` | Optional UV map name to set on the UV map node |

**Returns:** `tuple` — `(uvmap_node, texture_node, layer_number)` where `layer_number` is the new ink layer's index.

**Raises:** `ValueError` if the material is not MakeSkin or layered skin type.

---

#### get_number_of_ink_layers(material)

Count the number of ink layers present in a material by scanning for image texture nodes named `inkLayerNtex`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `material` | `bpy.types.Material` | — | The material to inspect |

**Returns:** `int` — The number of ink layers (0 if none).

**Raises:** `ValueError` if the material is not MakeSkin or layered skin type.

---

#### get_ink_layer_info(mesh_object, ink_layer=1)

Return information about the UV map and texture used by a specific ink layer.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The mesh object with the material |
| `ink_layer` | `int` | `1` | The ink layer number to query |

**Returns:** `tuple[str, str]` — `(uv_map_name, texture_name)`. The UV map name is empty if it's the default basemesh UV.

**Raises:** `ValueError` if the material type is unsupported or the layer nodes don't exist.

---

#### load_ink_layer(mesh_object, ink_layer_json_path)

Load an ink layer from a JSON definition file. The JSON must contain `focus`, `image_name`, and optionally `name` fields. If a focus is specified, the corresponding UV map is loaded from a compressed JSON file and added to the mesh. The ink layer nodes are created and the texture image is assigned.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mesh_object` | `bpy.types.Object` | — | The mesh object to add the ink layer to |
| `ink_layer_json_path` | `str` | — | Path to the ink layer JSON definition file |

**Returns:** `tuple` — `(uvmap_node, texture_node, ink_layer_id)`.

**Raises:** `ValueError` if the image file doesn't exist or the focus file can't be found.

---

#### remove_all_makeup(material, basemesh=None)

Remove all ink layers from a material. Deletes all nodes with names starting with `inkLayer` and reconnects the original diffuse color chain. Optionally removes ink layer UV maps from the basemesh.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `material` | `bpy.types.Material` | — | The material to clean up |
| `basemesh` | `bpy.types.Object` | `None` | Optional basemesh to remove ink layer UV maps from |

**Returns:** None

---

### Material I/O

#### as_blend_path(path)

Parse a blend file asset path string into its three components. The path format is `path/to/file.blend/Category/AssetName`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `path` | `str` | — | The blend file asset path string |

**Returns:** `tuple[str, str, str]` — `(blend_path, directory_name, asset_name)`.

---

#### save_material_in_blend_file(blender_object, path_to_blend_file, material_number=None, fake_user=False)

Save materials from an object to a `.blend` file. If `material_number` is `None`, saves all materials; otherwise, saves only the specified slot.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object whose materials to save |
| `path_to_blend_file` | `str` | — | Path to the destination `.blend` file |
| `material_number` | `int` | `None` | Specific material slot to save, or `None` for all |
| `fake_user` | `bool` | `False` | Whether to set fake user on saved materials |

**Returns:** None

---

#### load_material_from_blend_file(path, blender_object=None)

Load a material from a `.blend` file. The path should be in the format `file.blend/Material/MaterialName`. The material is made local after loading. Optionally assigns it to a Blender object.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `path` | `str` | — | Blend file asset path (see `as_blend_path`) |
| `blender_object` | `bpy.types.Object` | `None` | Optional object to assign the material to |

**Returns:** `bpy.types.Material` — The loaded material.

---

### Viewport Colors

#### get_skin_diffuse_color()

Return the static RGBA viewport display color for skin materials.

**Returns:** `list[float]` — `[0.721, 0.568, 0.431, 1.0]`

---

#### get_generic_bodypart_diffuse_color()

Return the static RGBA viewport display color for body part materials (eyebrows, eyelashes, hair, tongue).

**Returns:** `list[float]` — `[0.194, 0.030, 0.014, 1.0]`

---

#### get_generic_clothes_diffuse_color()

Return the static RGBA viewport display color for clothes materials.

**Returns:** `list[float]` — `[0.6, 0.6, 0.6, 1.0]`

---

#### get_eye_diffuse_color()

Return the static RGBA viewport display color for eye materials.

**Returns:** `list[float]` — `[0.95, 0.95, 0.95, 1.0]`

---

#### get_teeth_diffuse_color()

Return the static RGBA viewport display color for teeth materials.

**Returns:** `list[float]` — `[0.95, 0.95, 0.95, 1.0]`

---

#### get_diffuse_colors()

Return all static viewport display colors as a dictionary, keyed by MPFB object type.

**Returns:** `dict[str, list[float]]` — Maps object types (`"Eyes"`, `"Teeth"`, `"Basemesh"`, `"Clothes"`, etc.) to RGBA color lists.

---

## Examples

### Creating Materials for a Character

```python
from mpfb.services.materialservice import MaterialService

# Create a v2 skin material from an mhmat file
skin_mat = MaterialService.create_v2_skin_material(
    "CharacterSkin", basemesh, mhmat_file="/path/to/skin.mhmat"
)

# Create per-body-part material slots
MaterialService.create_and_assign_material_slots(basemesh, bodyproxy=proxy)
```

### Identifying and Modifying Materials

```python
from mpfb.services.materialservice import MaterialService

# Identify the material type
material = basemesh.data.materials[0]
mat_type = MaterialService.identify_material(material)
print(f"Material type: {mat_type}")  # e.g., "enhanced_skin"

# Set a normal map
MaterialService.set_normalmap(material, "/path/to/normal_map.png")
```

### Working with Ink Layers

```python
from mpfb.services.materialservice import MaterialService

material = basemesh.data.materials[0]

# Load an ink layer (tattoo, makeup, etc.)
uvmap, texture, layer_id = MaterialService.load_ink_layer(
    basemesh, "/path/to/tattoo.json"
)
print(f"Added ink layer {layer_id}")

# Check how many ink layers exist
num_layers = MaterialService.get_number_of_ink_layers(material)

# Remove all ink layers
MaterialService.remove_all_makeup(material, basemesh=basemesh)
```
