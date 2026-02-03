# NodeTreeService

NodeTreeService provides utility functions for working with Blender 4 style shader node tree interface sockets. It offers methods for querying, checking, and creating input and output sockets on node trees.

## Source

`src/mpfb/services/nodetreeservice.py`

## Dependencies

- `LogService` — logging

## Public API

### get_socket(node_tree, socket_name, in_out="INPUT")

Return the interface socket with the given name and direction, or `None`.

### get_output_socket(node_tree, socket_name)

Return the interface output socket with the given name, or `None`.

### get_input_socket(node_tree, socket_name)

Return the interface input socket with the given name, or `None`.

### has_socket(node_tree, socket_name, in_out="INPUT")

Return `True` if a socket with the given name and direction exists.

### has_input_socket(node_tree, socket_name)

Return `True` if an input socket with the given name exists.

### has_output_socket(node_tree, socket_name)

Return `True` if an output socket with the given name exists.

### create_socket(node_tree, socket_name, socket_type, in_out="INPUT")

Create a new socket with the given name, type, and direction, and return it.

### create_input_socket(node_tree, socket_name, socket_type)

Create a new input socket with the given name and type, and return it.

### create_output_socket(node_tree, socket_name, socket_type)

Create a new output socket with the given name and type, and return it.

## Example

```python
from mpfb.services.nodetreeservice import NodeTreeService

node_tree = bpy.data.node_groups["MyGroup"]
if not NodeTreeService.has_input_socket(node_tree, "Factor"):
    NodeTreeService.create_input_socket(node_tree, "Factor", "NodeSocketFloat")
```
