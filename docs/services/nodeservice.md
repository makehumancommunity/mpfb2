# NodeService

## Overview

NodeService provides a comprehensive collection of static methods for managing and manipulating Blender shader node trees and nodes. It is the primary service for all shader-related operations in MPFB, handling everything from creating individual nodes to applying complete material configurations from dictionary definitions.

The service supports two serialization formats: **v1** (legacy) and **v2** (current). The v2 format provides more complete node information including socket identifiers and attribute metadata, making it more robust across Blender versions. Both formats can be used to serialize node trees to JSON and recreate them programmatically.

Key capabilities include: **node tree lifecycle management** (creation, destruction, clearing), **node creation** (both generic and type-specific convenience methods), **node queries** (finding nodes by name, type, or class), **socket operations** (finding sockets, getting/setting default values), **link management** (creating and removing connections between nodes), and **bulk operations** (applying entire node tree configurations from dictionaries).

NodeService also manages MPFB's custom shader node groups. These are composite nodes that encapsulate common material patterns. The `ensure_v2_node_groups_exist()` method creates and validates all required node groups at addon startup.

All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/nodeservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.nodeservice")` |
| `NodeTreeService` | Node tree interface socket operations |

## Public API

### Node Tree Lifecycle

#### create_node_tree(node_tree_name, inputs=None, outputs=None)

Create a new shader node tree.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree_name` | `str` | — | Name for the new node tree |
| `inputs` | `list` | `None` | Optional input socket definitions (currently unused) |
| `outputs` | `list` | `None` | Optional output socket definitions (currently unused) |

**Returns:** `bpy.types.ShaderNodeTree` — The newly created node tree.

---

#### destroy_node_tree(node_tree)

Remove a shader node tree from Blender's data.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to remove |

**Returns:** None

---

#### clear_node_tree(node_tree, also_destroy_groups=False)

Delete all nodes in a node tree while preserving the tree instance.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to clear |
| `also_destroy_groups` | `bool` | `False` | Also destroy referenced node groups |

**Returns:** None

When `also_destroy_groups` is `True`, any `ShaderNodeGroup` nodes will have their referenced node trees renamed with `.unused` suffix to mark them for cleanup.

---

#### get_or_create_node_group(group_name)

Find or create a node tree by name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `group_name` | `str` | — | Name of the node group |

**Returns:** `bpy.types.ShaderNodeTree` — The existing or newly created node tree.

---

### V2 Node Groups

#### ensure_v2_node_groups_exist(fail_on_validation=False)

Ensure all MPFB v2 node groups exist, creating them if needed.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `fail_on_validation` | `bool` | `False` | Raise exception if validation fails |

**Returns:** None

Iterates over all registered v2 composite node wrappers, creates any missing node groups, and validates existing ones against their original definitions.

---

### Node Information Retrieval

#### get_v2_node_info(node)

Get detailed v2 format information about a node.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to inspect |

**Returns:** `dict` — Dictionary containing:
- `class`: Node class name
- `inputs`: Dict of input socket information (name, identifier, class, value_type, default_value)
- `outputs`: Dict of output socket information
- `attributes`: Dict of node attributes (name, class, value)

**Raises:** `ValueError` — If node is `None`.

---

#### get_node_info(node)

Get v1 format information about a node.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to inspect |

**Returns:** `dict` — Dictionary containing:
- `type`: Node class name
- `name`: Node name
- `label`: Node label
- `location`: Node position as list
- `values`: Dict of input socket default values
- `create`: Boolean (always `True`)

---

#### get_link_info(link)

Get information about a node link.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `link` | `bpy.types.NodeLink` | — | The link to inspect |

**Returns:** `dict` — Dictionary containing:
- `from_node`: Source node name
- `to_node`: Destination node name
- `from_socket`: Source socket name or index (if name is ambiguous)
- `to_socket`: Destination socket name or index (if name is ambiguous)

---

#### get_node_tree_as_dict(node_tree, recurse_groups=True, group_dict=None, recursion_level=0)

Serialize an entire node tree to a dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to serialize |
| `recurse_groups` | `bool` | `True` | Also serialize referenced node groups |
| `group_dict` | `dict` | `None` | Internal: shared group dictionary for recursion |
| `recursion_level` | `int` | `0` | Internal: current recursion depth |

**Returns:** `dict` — Dictionary containing:
- `nodes`: Dict of node information keyed by node name
- `links`: List of link information dicts
- `groups`: Dict of node group definitions (only at recursion level 0)

---

#### get_known_shader_node_classes()

Get a list of all known shader node classes.

**Returns:** `list` — List of shader node class objects.

---

### Socket Operations

#### get_socket_default_values(node)

Get default values for all input sockets of a node.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to query |

**Returns:** `dict` — Dictionary mapping socket names to default values.

Only returns values for `NodeSocketColor`, `NodeSocketFloatFactor`, and `NodeSocketFloat` socket types.

---

#### set_socket_default_values(node, values)

Set input socket default values from a dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to update |
| `values` | `dict` | — | Dictionary mapping socket names to values |

**Returns:** None

---

#### find_socket_default_value(node, socket_name)

Get the default value of a specific input socket.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to query |
| `socket_name` | `str` | — | Name of the input socket |

**Returns:** Value of the socket, or `None` if not found.

**Raises:** `ValueError` — If node is `None`.

---

#### find_input_socket_by_identifier_or_name(node, socket_identifier, socket_name=None, force_find_by_name=False)

Find an input socket by identifier or name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to search |
| `socket_identifier` | `str` | — | Socket identifier to find |
| `socket_name` | `str` | `None` | Alternative socket name |
| `force_find_by_name` | `bool` | `False` | Only search by name |

**Returns:** `bpy.types.NodeSocket` or `None`

For `ShaderNodeGroup` nodes, prefers name over identifier when `socket_name` is provided.

---

#### find_output_socket_by_identifier_or_name(node, socket_identifier, socket_name=None, force_find_by_name=False)

Find an output socket by identifier or name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to search |
| `socket_identifier` | `str` | — | Socket identifier to find |
| `socket_name` | `str` | `None` | Alternative socket name |
| `force_find_by_name` | `bool` | `False` | Only search by name |

**Returns:** `bpy.types.NodeSocket` or `None`

---

### Node Queries

#### find_node_by_name(node_tree, node_name)

Find a node by its name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to search |
| `node_name` | `str` | — | Name of the node |

**Returns:** `bpy.types.Node` or `None`

---

#### find_nodes_by_type_name(node_tree, type_name)

Find all nodes of a specific type.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to search |
| `type_name` | `str` | — | Node type name (class name or `node.type`) |

**Returns:** `list[bpy.types.Node]` — List of matching nodes.

---

#### find_first_node_by_type_name(node_tree, type_name)

Find the first node of a specific type.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to search |
| `type_name` | `str` | — | Node type name |

**Returns:** `bpy.types.Node` or `None`

---

#### find_first_group_node_by_tree_name(node_tree, tree_name)

Find the first group node using a specific node tree.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to search |
| `tree_name` | `str` | — | Name of the referenced node tree |

**Returns:** `bpy.types.ShaderNodeGroup` or `None`

---

#### find_nodes_by_class(node_tree, type_class)

Find all nodes of a specific class.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to search |
| `type_class` | `type` | — | Node class to find |

**Returns:** `list[bpy.types.Node]` — List of matching nodes.

---

#### find_first_node_by_class(node_tree, type_class)

Find the first node of a specific class.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to search |
| `type_class` | `type` | — | Node class to find |

**Returns:** `bpy.types.Node` or `None`

---

### Link Operations

#### find_node_linked_to_socket(node_tree, node_which_is_linked_to, name_of_socket)

Find the node that connects to a specific input socket.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree |
| `node_which_is_linked_to` | `bpy.types.Node` | — | The destination node |
| `name_of_socket` | `str` | — | Name of the input socket |

**Returns:** `bpy.types.Node` or `None` — The source node of the link.

**Raises:** `ValueError` — If node or socket name is `None`.

---

#### remove_link(node_tree, node_which_is_linked_to, name_of_socket)

Remove the link connected to a specific input socket.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree |
| `node_which_is_linked_to` | `bpy.types.Node` | — | The destination node |
| `name_of_socket` | `str` | — | Name of the input socket |

**Returns:** None

**Raises:** `ValueError` — If node or socket name is `None`.

---

#### add_link(node_tree, from_node, to_node, from_socket_name, to_socket_name)

Create a link between two nodes.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree |
| `from_node` | `bpy.types.Node` | — | The source node |
| `to_node` | `bpy.types.Node` | — | The destination node |
| `from_socket_name` | `str` | — | Name of the output socket |
| `to_socket_name` | `str` | — | Name of the input socket |

**Returns:** None

---

### Node Creation

#### create_node(node_tree, type_name, name=None, label=None, xpos=0, ypos=0)

Create a new node of the specified type.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree |
| `type_name` | `str` | — | Node type name (e.g., `"ShaderNodeBsdfPrincipled"`) |
| `name` | `str` | `None` | Optional node name |
| `label` | `str` | `None` | Optional node label |
| `xpos` | `float` | `0` | X position in node editor |
| `ypos` | `float` | `0` | Y position in node editor |

**Returns:** `bpy.types.Node` — The newly created node.

---

#### create_node_from_dict(node_tree, node_info)

Create a node from a dictionary definition.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree |
| `node_info` | `dict` | — | Node definition dictionary |

**Returns:** `bpy.types.Node` — The newly created node.

The dictionary should contain at minimum a `type` key with the node type name.

---

#### create_principled_node(node_tree, name=None, label=None, xpos=0, ypos=0)

Create a Principled BSDF node.

**Returns:** `bpy.types.ShaderNodeBsdfPrincipled`

---

#### create_bump_node(node_tree, name=None, label=None, xpos=0, ypos=0)

Create a Bump node.

**Returns:** `bpy.types.ShaderNodeBump`

---

#### create_normal_map_node(node_tree, name=None, label=None, xpos=0, ypos=0)

Create a Normal Map node.

**Returns:** `bpy.types.ShaderNodeNormalMap`

---

#### create_displacement_node(node_tree, name=None, label=None, xpos=0, ypos=0)

Create a Displacement node.

**Returns:** `bpy.types.ShaderNodeDisplacement`

---

#### create_mix_rgb_node(node_tree, name=None, label=None, xpos=0, ypos=0)

Create a Mix RGB node.

**Returns:** `bpy.types.ShaderNodeMixRGB`

---

#### create_value_node(node_tree, name=None, label=None, xpos=0, ypos=0, default_value=0.0)

Create a Value node.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `default_value` | `float` | `0.0` | Initial value (currently unused) |

**Returns:** `bpy.types.ShaderNodeValue`

---

#### create_attibute_node(node_tree, name=None, label=None, xpos=0, ypos=0, default_value="")

Create an Attribute node.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `default_value` | `str` | `""` | Initial attribute name (currently unused) |

**Returns:** `bpy.types.ShaderNodeAttribute`

---

#### create_image_texture_node(node_tree, name=None, label=None, xpos=0, ypos=0, image_path_absolute=None, colorspace="sRGB")

Create an Image Texture node with optional image.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `image_path_absolute` | `str` | `None` | Absolute path to image file |
| `colorspace` | `str` | `"sRGB"` | Color space for the image |

**Returns:** `bpy.types.ShaderNodeTexImage`

If `image_path_absolute` is provided, the image is loaded and assigned to the node.

---

### Image Handling

#### get_image_file_path(image_texture_node)

Get the file path of an image texture node's image.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `image_texture_node` | `bpy.types.ShaderNodeTexImage` | — | The image texture node |

**Returns:** `str` or `None` — Normalized absolute path, or `None` if not available.

---

#### set_image_in_image_node(node, file_name, colorspace=None)

Set the image in an image texture node.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.ShaderNodeTexImage` | — | The image texture node |
| `file_name` | `str` | — | Path to the image file |
| `colorspace` | `str` | `None` | Color space (defaults to `"sRGB"`) |

**Returns:** None

Loads the image if not already in Blender's data, and applies the colorspace setting.

---

#### update_tex_image_with_settings_from_dict(node, node_info)

Update an image texture node from a dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.ShaderNodeTexImage` | — | The image texture node |
| `node_info` | `dict` | — | Dictionary with `filename` and optional `colorspace` |

**Returns:** None

---

### Bulk Operations

#### update_node_with_settings_from_dict(node, node_info)

Update a node's settings from a dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to update |
| `node_info` | `dict` | — | Dictionary with node settings |

**Returns:** None

Handles special cases for various node types including `ShaderNodeGroup`, `ShaderNodeTexImage`, `ShaderNodeMath`, `ShaderNodeMixRGB`, and `ShaderNodeValue`.

---

#### apply_node_tree_from_dict(target_node_tree, dict_with_node_tree, wipe_node_tree=False)

Apply an entire node tree configuration from a dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `target_node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to update |
| `dict_with_node_tree` | `dict` | — | Complete node tree definition |
| `wipe_node_tree` | `bool` | `False` | Clear existing nodes first |

**Returns:** None

**Raises:** `ValueError` — If node tree definitions are invalid or links are broken.

Creates all node groups first, then creates nodes, then creates links.

---

## Examples

### Creating a Simple Material

```python
from mpfb.services.nodeservice import NodeService
import bpy

# Create a new material
material = bpy.data.materials.new("MyMaterial")
material.use_nodes = True
node_tree = material.node_tree

# Clear default nodes
NodeService.clear_node_tree(node_tree)

# Create nodes
output = NodeService.create_node(node_tree, "ShaderNodeOutputMaterial", xpos=300)
principled = NodeService.create_principled_node(node_tree, xpos=0, ypos=0)

# Connect them
NodeService.add_link(node_tree, principled, output, "BSDF", "Surface")
```

### Adding Texture Support

```python
from mpfb.services.nodeservice import NodeService

# Add an image texture
diffuse_tex = NodeService.create_image_texture_node(
    node_tree,
    name="DiffuseTexture",
    xpos=-300,
    image_path_absolute="/path/to/diffuse.png",
    colorspace="sRGB"
)

# Connect to principled BSDF
principled = NodeService.find_first_node_by_type_name(node_tree, "ShaderNodeBsdfPrincipled")
NodeService.add_link(node_tree, diffuse_tex, principled, "Color", "Base Color")
```

### Serializing and Recreating Node Trees

```python
from mpfb.services.nodeservice import NodeService
import json

# Serialize the node tree
material = bpy.data.materials["MyMaterial"]
tree_dict = NodeService.get_node_tree_as_dict(material.node_tree)

# Save to file
with open("material.json", "w") as f:
    json.dump(tree_dict, f, indent=2)

# Later, recreate on another material
new_material = bpy.data.materials.new("CopiedMaterial")
new_material.use_nodes = True
NodeService.apply_node_tree_from_dict(
    new_material.node_tree,
    tree_dict,
    wipe_node_tree=True
)
```

### Finding and Modifying Nodes

```python
from mpfb.services.nodeservice import NodeService

node_tree = material.node_tree

# Find all image texture nodes
tex_nodes = NodeService.find_nodes_by_type_name(node_tree, "ShaderNodeTexImage")
for tex in tex_nodes:
    print(f"Texture: {tex.name}, Image: {NodeService.get_image_file_path(tex)}")

# Get socket values
principled = NodeService.find_first_node_by_type_name(node_tree, "ShaderNodeBsdfPrincipled")
roughness = NodeService.find_socket_default_value(principled, "Roughness")
print(f"Roughness: {roughness}")

# Set socket values
NodeService.set_socket_default_values(principled, {
    "Roughness": 0.5,
    "Metallic": 0.0
})
```

### Working with Node Groups

```python
from mpfb.services.nodeservice import NodeService

# Find or create a node group
skin_group = NodeService.get_or_create_node_group("MPFB_Skin")

# Find all uses of a node group in a material
material = bpy.data.materials["SkinMaterial"]
group_nodes = NodeService.find_nodes_by_type_name(
    material.node_tree, "ShaderNodeGroup"
)
for gn in group_nodes:
    if gn.node_tree.name == "MPFB_Skin":
        print(f"Found skin group: {gn.name}")
```
