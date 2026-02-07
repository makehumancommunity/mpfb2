# HairEditorService

## Overview

This service is experimental and only relevant when working with the hair/fur editor. It is unlikely you would use it from anywhere else in the code.

HairEditorService provides utility functions for the MPFB hair editor system. It manages the discovery of hair and fur asset blend files, checks whether these assets are installed, and provides methods for manipulating shader node links within hair materials.

Hair and fur assets are distributed as `.blend` files located in a `haireditor` subdirectory under the hair data folder. The service searches for these files first in the user data directory and then falls back to the system (built-in) data directory. The shader manipulation methods operate on Principled BSDF nodes inside a "Hair shader EEVEE" node group, allowing texture nodes to be temporarily connected to or disconnected from the shader's base color inputs while preserving the original link state for later restoration.

All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/haireditorservices.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.haireditorservice")` |
| `LocationService` | Resolving user data and system data paths for hair blend files |

## Public API

### Asset Paths

#### get_hair_blend_path()

Get the absolute path to the hair blend file. Checks the user data directory first (`<user_data>/hair/haireditor/hair.blend`), then falls back to the system data directory.

**Returns:** `str` or `None` — The absolute path to the hair blend file, or `None` if not found.

---

#### get_fur_blend_path()

Get the absolute path to the fur blend file. Checks the user data directory first (`<user_data>/hair/haireditor/fur.blend`), then falls back to the system data directory.

**Returns:** `str` or `None` — The absolute path to the fur blend file, or `None` if not found.

---

### Asset Installation

#### is_hair_asset_installed()

Check whether the hair blend file exists in any of the searched locations.

**Returns:** `bool` — `True` if the hair blend file is found.

---

#### is_fur_asset_installed()

Check whether the fur blend file exists in any of the searched locations.

**Returns:** `bool` — `True` if the fur blend file is found.

---

### Shader Links

#### join_texture_node_to_shader(img_node, shader_nodes, group_node, links, storage_key, store_links)

Connect a texture image node to the base color input of one or more Principled BSDF shader nodes inside the "Hair shader EEVEE" node group. Before connecting the new links, any existing links to the base color inputs are removed. If `store_links` is `True`, the previous link state is serialized as JSON and stored as a custom property on the group node so it can be restored later.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `img_node` | `bpy.types.ShaderNode` | — | The image texture node to connect; pass `None` to only disconnect existing links |
| `shader_nodes` | `list[bpy.types.ShaderNode]` | — | List of Principled BSDF nodes to connect to |
| `group_node` | `bpy.types.ShaderNodeGroup` | — | The Hair shader group node, used to store link state |
| `links` | `bpy.types.NodeLinks` | — | The node tree's links collection |
| `storage_key` | `str` | — | Custom property key name for storing the previous link state |
| `store_links` | `bool` | — | Whether to save the previous links for later restoration |

**Returns:** None

---

#### restore_shader_links(img_node, shader_nodes, group_node, nodes, links, storage_key)

Restore the original color links to Principled BSDF shaders inside the "Hair shader EEVEE" node group after a texture override has been turned off. Removes any links from the specified image node, then re-creates the original links from the saved state stored by `join_texture_node_to_shader`. The saved state is deleted from the group node after restoration.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `img_node` | `bpy.types.ShaderNode` | — | The image texture node to disconnect; pass `None` to skip disconnection |
| `shader_nodes` | `list[bpy.types.ShaderNode]` | — | List of Principled BSDF nodes whose inputs to restore |
| `group_node` | `bpy.types.ShaderNodeGroup` | — | The Hair shader group node with saved link state |
| `nodes` | `bpy.types.Nodes` | — | The node tree's nodes collection, used to look up source nodes by name |
| `links` | `bpy.types.NodeLinks` | — | The node tree's links collection |
| `storage_key` | `str` | — | Custom property key name where the link state was stored |

**Returns:** None

---

## Examples

### Checking for Hair Assets

```python
from mpfb.services.haireditorservices import HairEditorService

# Check availability before attempting to use hair assets
if HairEditorService.is_hair_asset_installed():
    hair_path = HairEditorService.get_hair_blend_path()
    print(f"Hair blend file: {hair_path}")

if HairEditorService.is_fur_asset_installed():
    fur_path = HairEditorService.get_fur_blend_path()
    print(f"Fur blend file: {fur_path}")
```

### Connecting a Texture to Hair Shaders

```python
from mpfb.services.haireditorservices import HairEditorService

# Inside a "Hair shader EEVEE" node group:
# Connect an image texture to the principled shader base color inputs
HairEditorService.join_texture_node_to_shader(
    img_node=texture_node,
    shader_nodes=principled_nodes,
    group_node=hair_group_node,
    links=node_tree.links,
    storage_key="prev_color_links",
    store_links=True
)

# Later, restore the original shader links
HairEditorService.restore_shader_links(
    img_node=texture_node,
    shader_nodes=principled_nodes,
    group_node=hair_group_node,
    nodes=node_tree.nodes,
    links=node_tree.links,
    storage_key="prev_color_links"
)
```
