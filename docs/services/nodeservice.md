# NodeService

NodeService provides a comprehensive collection of static methods for managing and manipulating Blender shader node trees and nodes. It includes functionality for creating and destroying node trees, retrieving node information, managing node groups, creating specific node types, and applying full node tree configurations from dictionaries.

## Source

`src/mpfb/services/nodeservice.py`

## Dependencies

- `LogService` — logging
- `NodeTreeService` — node tree interface socket operations

## Public API

### create_node_tree(node_tree_name, inputs=None, outputs=None)

Create a new shader node tree with the given name and optional input/output sockets.

### destroy_node_tree(node_tree)

Remove a shader node tree from Blender's data.

### ensure_v2_node_groups_exist(fail_on_validation=False)

Iterate over all v2 node groups and ensure they exist, creating them if needed.

### get_v2_node_info(node)

Return a v2 model dict with node info including socket values and attributes.

### get_known_shader_node_classes()

Retrieve a list of known shader node classes.

### get_node_info(node)

Return a v1 model dict with node info including inputs, outputs, and attributes.

### get_socket_default_values(node)

Return a dict of default values for all input sockets of a node.

### set_socket_default_values(node, values)

Set a node's input socket default values from a provided dict.

### get_link_info(link)

Return a dict describing a specific node link.

### get_node_tree_as_dict(node_tree, recurse_groups=True, group_dict=None, recursion_level=0)

Return a dict describing the entire node tree including definitions, groups, and links.

### clear_node_tree(node_tree, also_destroy_groups=False)

Delete all nodes in a node tree while preserving the tree instance.

### set_image_in_image_node(node, file_name, colorspace=None)

Update an image node with the provided filename and colorspace.

### update_tex_image_with_settings_from_dict(node, node_info)

Set filename and colorspace info in an image texture node from a dict.

### update_node_with_settings_from_dict(node, node_info)

Set node attributes and input socket values from a provided dict.

### get_or_create_node_group(group_name)

Find an existing node tree by name or create it if it does not exist.

### find_node_by_name(node_tree, node_name)

Find a node with the given name in a node tree.

### find_nodes_by_type_name(node_tree, type_name)

Return all nodes of the given type in a node tree.

### find_input_socket_by_identifier_or_name(node, socket_identifier, socket_name=None, force_find_by_name=False)

Return an input socket matching the given identifier or name.

### find_output_socket_by_identifier_or_name(node, socket_identifier, socket_name=None, force_find_by_name=False)

Return an output socket matching the given identifier or name.

### find_first_node_by_type_name(node_tree, type_name)

Find the first node of the given type in a node tree.

### find_first_group_node_by_tree_name(node_tree, tree_name)

Find the first `ShaderNodeGroup` using the indicated node tree name.

### find_nodes_by_class(node_tree, type_class)

Return all nodes of the given type class in a node tree.

### find_first_node_by_class(node_tree, type_class)

Find the first node of the given type class in a node tree.

### find_socket_default_value(node, socket_name)

Return the default value of a node's input socket with the given name.

### find_node_linked_to_socket(node_tree, node_which_is_linked_to, name_of_socket)

Return the node that links to the specified input socket.

### remove_link(node_tree, node_which_is_linked_to, name_of_socket)

Remove the link connected to the specified input socket.

### add_link(node_tree, from_node, to_node, from_socket_name, to_socket_name)

Add a link between two nodes.

### get_image_file_path(image_texture_node)

Return the normalized file path of the image referenced by an image texture node.

### create_node(node_tree, type_name, name=None, label=None, xpos=0, ypos=0)

Create a new node of the given type in the node tree.

### create_node_from_dict(node_tree, node_info)

Create a new node based on information in a provided dict.

### create_principled_node(node_tree, name=None, label=None, xpos=0, ypos=0)

Create a new Principled BSDF node.

### create_bump_node(node_tree, name=None, label=None, xpos=0, ypos=0)

Create a new bump map node.

### create_normal_map_node(node_tree, name=None, label=None, xpos=0, ypos=0)

Create a new normal map node.

### create_displacement_node(node_tree, name=None, label=None, xpos=0, ypos=0)

Create a new displacement map node.

### create_mix_rgb_node(node_tree, name=None, label=None, xpos=0, ypos=0)

Create a new mix RGB node.

### create_value_node(node_tree, name=None, label=None, xpos=0, ypos=0, default_value=0.0)

Create a new value node with an optional default.

### create_attibute_node(node_tree, name=None, label=None, xpos=0, ypos=0, default_value="")

Create a new attribute node with an optional default.

### create_image_texture_node(node_tree, name=None, label=None, xpos=0, ypos=0, image_path_absolute=None, colorspace="sRGB")

Create a new image texture node with optional image path and colorspace.

### apply_node_tree_from_dict(target_node_tree, dict_with_node_tree, wipe_node_tree=False)

Apply an entire node tree configuration from a dict, optionally wiping the existing tree first.

## Example

```python
from mpfb.services.nodeservice import NodeService

material = bpy.data.materials["MyMaterial"]
node_tree = material.node_tree
principled = NodeService.create_principled_node(node_tree, xpos=-200, ypos=0)
tree_dict = NodeService.get_node_tree_as_dict(node_tree)
```
