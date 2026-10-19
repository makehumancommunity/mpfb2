# NodeService

## Overview

NodeService provides a comprehensive collection of static methods for managing and manipulating Blender shader node trees and nodes. It is the primary service for all shader-related operations in MPFB, handling everything from creating individual nodes to applying complete material configurations from dictionary definitions.

The service supports two serialization formats: **v1** (legacy) and **v2** (current). The v2 format provides more complete node information including socket identifiers and attribute metadata, making it more robust across Blender versions. Both formats can be used to serialize node trees to JSON and recreate them programmatically.

Key capabilities include: **node tree lifecycle management** (creation, destruction, clearing), **node creation** (both generic and type-specific convenience methods), **node queries** (finding nodes by name, type, or class), **socket operations** (finding sockets, getting/setting default values), **link management** (creating and removing connections between nodes), and **bulk operations** (applying entire node tree configurations from dictionaries).

NodeService also manages MPFB's custom shader node groups. These are composite nodes that encapsulate common material patterns. The `ensure_v2_node_groups_exist()` method creates and validates all required node groups at addon startup.

Two things are worth knowing before calling anything here. First, **every `find_*` method answers `bpy.types.Node | None` (or an empty list), and `add_link()` does not check the nodes or sockets it is given** — a name which does not exist reaches `links.new()` as `None` and raises `TypeError` naming neither of the two names that were wrong. Callers in MPFB rely on a material's own structure to guarantee the lookup instead of testing it, which is why several of them carry a `typing.cast` at the call rather than a guard.

Second, the node tree arguments are typed `bpy.types.NodeTree`, not `bpy.types.ShaderNodeTree`. Nothing in this service needs the shader subclass, and the common argument is `material.node_tree`, which the Blender stubs declare as `ShaderNodeTree | None` — so a caller reading it off a material passes it through a cast for the `None`, not for the subclass.

> **`get_node_tree_as_dict()` cannot serialise a tree which contains a node group.** Its group branch reads `NodeTree.inputs` and `NodeTree.outputs`, which Blender replaced with `NodeTree.interface` in 4.0 — two minor versions below this addon's own floor. The reads raise `AttributeError` on every supported version, verified on 4.2.1 and on 5.1. See the method entry below.

All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/nodeservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.nodeservice")` |
| `NodeTreeService` | Node tree interface socket operations, and the `SocketInOut` literal |

## Module-Level Types

Declared in `nodeservice.py`:

| Name | Definition | What it is |
|------|------------|------------|
| `NodeInfoV2` | `dict[str, Any]` | The v2 description of one node: `class`, `inputs`, `outputs` and `attributes`. Only the developer operators in the UI layer read one, which is why it is local rather than shared |
| `LinkInfo` | `dict[str, str \| int]` | One link: `from_node`, `to_node`, `from_socket`, `to_socket`. The two socket entries are names, or the socket index where the node carries more than one socket of that name |

Declared in `src/mpfb/types.py`, because they cross into `MaterialService`, `HumanService` and the material entities:

| Name | Definition | What it is |
|------|------------|------------|
| `NodeInfo` | `dict[str, Any]` | The v1 description of one node, and the shape the JSON templates under `data/node_trees` are written in |
| `NodeTreeDict` | `dict[str, Any]` | A whole tree: `nodes`, `links` and, at the outermost level only, `groups` |
| `SocketValues` | `dict[str, Any]` | Input socket name to default value, for the three socket classes this service reads and writes |

Imported from `NodeTreeService`:

| Name | Definition | What it is |
|------|------------|------------|
| `SocketInOut` | `Literal["INPUT", "OUTPUT"]` | The direction argument of the two private interface socket helpers |

## Public API

### Node Tree Lifecycle

#### create_node_tree(node_tree_name, inputs=None, outputs=None)

Create a new shader node tree.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree_name` | `str` | — | Name for the new node tree |
| `inputs` | `list[Any] \| None` | `None` | Accepted and never read |
| `outputs` | `list[Any] \| None` | `None` | Accepted and never read |

**Returns:** `bpy.types.ShaderNodeTree` — The newly created node tree.

---

#### destroy_node_tree(node_tree)

Remove a shader node tree from Blender's data.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.NodeTree` | — | The node tree to remove |

**Returns:** None

---

#### clear_node_tree(node_tree, also_destroy_groups=False)

Delete all nodes in a node tree while preserving the tree instance.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.NodeTree` | — | The node tree to clear |
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

**Returns:** `NodeInfoV2` — Dictionary containing:
- `class`: Node class name
- `inputs`: Dict of input socket information (name, identifier, class, value_type, default_value), plus `min_value` and `max_value` for a float socket on a group node
- `outputs`: Dict of output socket information
- `attributes`: Dict of node attributes (name, class, value)

**Raises:** `ValueError` — If node is `None`.

The `min_value`/`max_value` lookup is guarded by `hasattr(node, "node_tree")` rather than by the node's class, so a node type which carries an empty `node_tree` — a group node added but never assigned a tree — raises `AttributeError` there rather than being skipped.

---

#### get_node_info(node)

Get v1 format information about a node.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to inspect |

**Returns:** `NodeInfo` — Dictionary containing:
- `type`: Node class name
- `name`: Node name
- `label`: Node label
- `location`: Node position as list
- `values`: `SocketValues` — input socket default values
- `create`: Boolean (always `True`)

Plus, for the node types it knows: `filename` and `colorspace` for a `ShaderNodeTexImage`, `operation` and `use_clamp` for a `ShaderNodeMath`, `operation` for a `ShaderNodeVectorMath`, and `value` for a `ShaderNodeValue`.

---

#### get_link_info(link)

Get information about a node link.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `link` | `bpy.types.NodeLink` | — | The link to inspect |

**Returns:** `LinkInfo` — Dictionary containing:
- `from_node`: Source node name
- `to_node`: Destination node name
- `from_socket`: Source socket name or index (if name is ambiguous)
- `to_socket`: Destination socket name or index (if name is ambiguous)

All four endpoints of a `bpy.types.NodeLink` are declared optional by the stubs, and the RNA agrees on both supported Blender versions, but a link which is actually in a tree's `links` collection always has all four — which is the only way one reaches this method.

---

#### get_node_tree_as_dict(node_tree, recurse_groups=True, group_dict=None, recursion_level=0)

Serialize an entire node tree to a dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.NodeTree` | — | The node tree to serialize |
| `recurse_groups` | `bool` | `True` | Also serialize referenced node groups |
| `group_dict` | `dict[str, NodeTreeDict] \| None` | `None` | Internal: shared group dictionary for recursion |
| `recursion_level` | `int` | `0` | Internal: current recursion depth |

**Returns:** `NodeTreeDict` — Dictionary containing:
- `nodes`: Dict of `NodeInfo` keyed by node name
- `links`: List of `LinkInfo` dicts
- `groups`: Dict of node group definitions (only at recursion level 0)

> **This method cannot serialise a tree which contains a `ShaderNodeGroup`.** Once it has recursed into the group's own tree it reads `node.node_tree.inputs` and `node.node_tree.outputs` to record the group's interface. Neither attribute exists: Blender replaced them with `NodeTree.interface` in 4.0, and neither name appears in `NodeTree.bl_rna.properties` on 4.2.1 or on 5.1, so both reads raise `AttributeError`. `NodeTreeService.get_socket()` walks `interface.items_tree`, which is the form that works, and is what the three statements in that branch would have to be rewritten against. Until then, the method is usable only on a flat tree, or with `recurse_groups=False` — which skips the whole branch, interface records included.

---

#### get_known_shader_node_classes()

Get a list of all known shader node classes.

**Returns:** `list[type[bpy.types.ShaderNode]]` — The classes themselves, not their names: every class in `bpy.types` which has `bpy.types.ShaderNode` as a *direct* base. The list is built once at import time, so a node class registered later by another add-on is not in it.

---

### Socket Operations

#### get_socket_default_values(node)

Get default values for all input sockets of a node.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to query |

**Returns:** `SocketValues` — Dictionary mapping socket names to default values: a `float` for the two float socket classes and a four element `list[float]` for a colour.

Only returns values for `NodeSocketColor`, `NodeSocketFloatFactor`, and `NodeSocketFloat` socket types. A node with no `inputs` attribute at all yields an empty dict rather than raising.

---

#### set_socket_default_values(node, values)

Set input socket default values from a dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to update |
| `values` | `SocketValues` | — | Dictionary mapping socket names to values |

**Returns:** None

Names in `values` which the node does not carry are ignored silently, and a node with no `inputs` attribute is a logged no-op rather than an error.

---

#### find_socket_default_value(node, socket_name)

Get the default value of a specific input socket.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to query |
| `socket_name` | `str` | — | Name of the input socket |

**Returns:** `Any` — whatever the named socket holds, which is a `float`, a `bool`, a `str` or a colour depending entirely on which socket the caller asked for; `Any` is therefore the deliberate answer rather than a placeholder. `None` is also a genuine return, for a node with no inputs or no input of that name.

**Raises:** `ValueError` — If node is `None`.

---

#### find_input_socket_by_identifier_or_name(node, socket_identifier, socket_name=None, force_find_by_name=False)

Find an input socket by identifier or name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to search |
| `socket_identifier` | `str` | — | Socket identifier to find |
| `socket_name` | `str \| None` | `None` | Alternative socket name |
| `force_find_by_name` | `bool` | `False` | Only search by name |

**Returns:** `bpy.types.NodeSocket | None`

For `ShaderNodeGroup` nodes, prefers name over identifier when `socket_name` is provided.

---

#### find_output_socket_by_identifier_or_name(node, socket_identifier, socket_name=None, force_find_by_name=False)

Find an output socket by identifier or name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to search |
| `socket_identifier` | `str` | — | Socket identifier to find |
| `socket_name` | `str \| None` | `None` | Alternative socket name |
| `force_find_by_name` | `bool` | `False` | Only search by name |

**Returns:** `bpy.types.NodeSocket | None`

---

### Node Queries

#### find_node_by_name(node_tree, node_name)

Find a node by its name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.NodeTree` | — | The node tree to search |
| `node_name` | `str` | — | Name of the node |

**Returns:** `bpy.types.Node | None`

---

#### find_nodes_by_type_name(node_tree, type_name)

Find all nodes of a specific type.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.NodeTree` | — | The node tree to search |
| `type_name` | `str` | — | Node type name (class name or `node.type`) |

**Returns:** `list[bpy.types.Node]` — List of matching nodes.

---

#### find_first_node_by_type_name(node_tree, type_name)

Find the first node of a specific type.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.NodeTree` | — | The node tree to search |
| `type_name` | `str` | — | Node type name |

**Returns:** `bpy.types.Node | None`

---

#### find_first_group_node_by_tree_name(node_tree, tree_name)

Find the first group node using a specific node tree.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.NodeTree` | — | The node tree to search |
| `tree_name` | `str` | — | Name of the referenced node tree |

**Returns:** `bpy.types.ShaderNodeGroup | None`

---

#### find_nodes_by_class(node_tree, type_class)

Find all nodes of a specific class.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.NodeTree` | — | The node tree to search |
| `type_class` | `type` | — | Node class to find, passed straight to `isinstance()` |

**Returns:** `list[bpy.types.Node]` — List of matching nodes.

---

#### find_first_node_by_class(node_tree, type_class)

Find the first node of a specific class.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.NodeTree` | — | The node tree to search |
| `type_class` | `type` | — | Node class to find, passed straight to `isinstance()` |

**Returns:** `bpy.types.Node | None`

---

### Link Operations

#### find_node_linked_to_socket(node_tree, node_which_is_linked_to, name_of_socket)

Find the node that connects to a specific input socket.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.NodeTree` | — | The node tree |
| `node_which_is_linked_to` | `bpy.types.Node` | — | The destination node |
| `name_of_socket` | `str` | — | Name of the input socket |

**Returns:** `bpy.types.Node | None` — The source node of the link.

**Raises:** `ValueError` — If node or socket name is `None`.

---

#### remove_link(node_tree, node_which_is_linked_to, name_of_socket)

Remove the link connected to a specific input socket.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.NodeTree` | — | The node tree |
| `node_which_is_linked_to` | `bpy.types.Node` | — | The destination node |
| `name_of_socket` | `str` | — | Name of the input socket |

**Returns:** None

**Raises:** `ValueError` — If node or socket name is `None`.

---

#### add_link(node_tree, from_node, to_node, from_socket_name, to_socket_name)

Create a link between two nodes.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.NodeTree` | — | The node tree |
| `from_node` | `bpy.types.Node` | — | The source node |
| `to_node` | `bpy.types.Node` | — | The destination node |
| `from_socket_name` | `str` | — | Name of the output socket |
| `to_socket_name` | `str` | — | Name of the input socket |

**Returns:** None

> **Neither socket name is checked.** Each is resolved with the socket finder above, which answers `None` for a name the node does not carry, and the result goes straight to `links.new()` — which raises `TypeError` without saying which of the two names was wrong. The same applies to the nodes: `add_link()` does not test them, so a caller passing an unguarded `find_*` result reaches the same `TypeError`.

---

### Node Creation

#### create_node(node_tree, type_name, name=None, label=None, xpos=0, ypos=0)

Create a new node of the specified type.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.NodeTree` | — | The node tree |
| `type_name` | `str` | — | Node type name (e.g., `"ShaderNodeBsdfPrincipled"`) |
| `name` | `str \| None` | `None` | Optional node name |
| `label` | `str \| None` | `None` | Optional node label |
| `xpos` | `float` | `0` | X position in node editor |
| `ypos` | `float` | `0` | Y position in node editor |

**Returns:** `bpy.types.Node` — The newly created node. The base class, not the subclass the type name selects: a caller which needs the subclass narrows it with a `typing.cast`, which is what the type-specific factories below do.

---

#### create_node_from_dict(node_tree, node_info)

Create a node from a dictionary definition.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.NodeTree` | — | The node tree |
| `node_info` | `NodeInfo` | — | Node definition dictionary |

**Returns:** `bpy.types.Node` — The newly created node.

The dictionary should contain at minimum a `type` key with the node type name.

---

The six factories below take the same arguments as `create_node()` — `node_tree`, `name`, `label`, `xpos`, `ypos` — and differ only in the type name they pass and the subclass they narrow the result to. Each one is a `typing.cast` over `create_node()`, which is as safe as the type name is correct.

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
| `default_value` | `float` | `0.0` | Accepted and never applied; set the node's output socket afterwards to give it a value |

**Returns:** `bpy.types.ShaderNodeValue`

---

#### create_attibute_node(node_tree, name=None, label=None, xpos=0, ypos=0, default_value="")

Create an Attribute node. The method name is misspelled — "attibute" — and is kept as it is because renaming it would break callers.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `default_value` | `str` | `""` | Accepted and never applied; set `attribute_name` on the returned node instead |

**Returns:** `bpy.types.ShaderNodeAttribute`

---

#### create_image_texture_node(node_tree, name=None, label=None, xpos=0, ypos=0, image_path_absolute=None, colorspace="sRGB")

Create an Image Texture node with optional image.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `image_path_absolute` | `str \| None` | `None` | Absolute path to image file |
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

**Returns:** `str | None` — Normalized absolute path, or `None` if the node has no image, the image has no file path, or the path is not a file.

---

#### set_image_in_image_node(node, file_name, colorspace=None)

Set the image in an image texture node.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.ShaderNodeTexImage` | — | The image texture node |
| `file_name` | `str` | — | Path to the image file |
| `colorspace` | `str \| None` | `None` | Color space; `None` means `"sRGB"` |

**Returns:** None

Loads the image if not already in Blender's data, and applies the colorspace setting. An empty or whitespace-only `file_name`, and a path which does not exist, are both logged and returned from without touching the node. A colorspace name Blender does not know is caught and logged, leaving whatever the image already had.

---

#### update_tex_image_with_settings_from_dict(node, node_info)

Update an image texture node from a dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.ShaderNodeTexImage` | — | The image texture node |
| `node_info` | `NodeInfo` | — | Dictionary with `filename` and optional `colorspace` |

**Returns:** None

---

### Bulk Operations

#### update_node_with_settings_from_dict(node, node_info)

Update a node's settings from a dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node` | `bpy.types.Node` | — | The node to update |
| `node_info` | `NodeInfo` | — | Dictionary with node settings |

**Returns:** None

Handles special cases for various node types including `ShaderNodeGroup`, `ShaderNodeTexImage`, `ShaderNodeMath`, `ShaderNodeMixRGB`, and `ShaderNodeValue`. Each branch is selected on `node_info["type"]` and then writes a property declared only on that subclass, so a dict whose `type` disagrees with the node it is applied to is an `AttributeError`. One pairing is worth noting: `ShaderNodeMath` and `ShaderNodeVectorMath` share a branch, but only the former has `use_clamp`, so a vector maths entry carrying `use_clamp` fails there.

---

#### apply_node_tree_from_dict(target_node_tree, dict_with_node_tree, wipe_node_tree=False)

Apply an entire node tree configuration from a dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `target_node_tree` | `bpy.types.NodeTree` | — | The node tree to update |
| `dict_with_node_tree` | `NodeTreeDict` | — | Complete node tree definition |
| `wipe_node_tree` | `bool` | `False` | Clear existing nodes first |

**Returns:** None

**Raises:** `ValueError` — If node tree definitions are invalid or links are broken.

Creates all node groups first, then creates nodes, then creates links. A link whose target socket already has one raises; a link whose socket does not exist at all is only logged.

---

## Private helpers

Not part of the API, but worth knowing about if you are reading the source.

| Method | Note |
|--------|------|
| `_has_socket(node_tree, socket_name, in_out="INPUT")` | A duplicate of `NodeTreeService.has_socket()`, which it predates. Prefer the service. |
| `_create_socket(node_tree, socket_name, socket_type, in_out="INPUT")` | A duplicate of `NodeTreeService.create_socket()`, same story. |
| `_find_socket_by_identifier_or_name(...)` | The body behind the two public socket finders. For a `ShaderNodeGroup` it prefers the name over the identifier; for everything else the identifier wins unless `force_find_by_name` is set. |
| `_ensure_group_interfaces_exist(dict_with_node_tree, force_wipe_group_node_trees=False)` | Creates each group named in the dict's `groups`, gives it Group Input and Group Output nodes, and adds the declared interface sockets. Marks each group `pre_existing` so `apply_node_tree_from_dict()` knows not to rebuild it. |
| `_add_tex_image_info(node, node_info)` | Writes `colorspace` and `filename` into a `NodeInfo` for an image texture node. |

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

This only works for a material whose node tree is flat. A tree holding a `ShaderNodeGroup` — which every MPFB
enhanced-skin or layered-skin material does — raises `AttributeError` out of `get_node_tree_as_dict()`; see that
method's entry above.

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
    # node_tree is empty for a group node which has never been assigned one
    if gn.node_tree and gn.node_tree.name == "MPFB_Skin":
        print(f"Found skin group: {gn.name}")

# Or, more directly:
skin_node = NodeService.find_first_group_node_by_tree_name(material.node_tree, "MPFB_Skin")
```
