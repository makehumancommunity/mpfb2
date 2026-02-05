# NodeTreeService

## Overview

NodeTreeService provides utility functions for working with Blender 4+ style shader node tree interface sockets. It offers a clean API for querying, checking, and creating input and output sockets on node trees (node groups).

In Blender 4.0, the node tree interface API changed significantly. Node group inputs and outputs are now managed through `node_tree.interface.items_tree` rather than the older `node_tree.inputs` and `node_tree.outputs` collections. NodeTreeService abstracts these changes, providing a consistent interface for socket operations.

The service is focused specifically on **node tree interface sockets**—the external sockets visible when a node group is used as a node in another tree. For internal node socket operations (the actual connections between nodes within a tree), see NodeService.

NodeTreeService is a dependency of NodeService and is used whenever node groups need their interfaces configured or queried.

All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/nodetreeservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.nodetreeservice")` |

## Socket Types

Common socket type identifiers for use with `create_socket()`:

| Type | Description |
|------|-------------|
| `NodeSocketFloat` | Scalar float value |
| `NodeSocketFloatFactor` | Float clamped to 0-1 range |
| `NodeSocketInt` | Integer value |
| `NodeSocketBool` | Boolean value |
| `NodeSocketVector` | 3D vector |
| `NodeSocketColor` | RGBA color |
| `NodeSocketShader` | Shader output |
| `NodeSocketString` | Text string |
| `NodeSocketImage` | Image reference |
| `NodeSocketGeometry` | Geometry data |
| `NodeSocketCollection` | Collection reference |
| `NodeSocketObject` | Object reference |

## Public API

### Socket Queries

#### get_socket(node_tree, socket_name, in_out="INPUT")

Get an interface socket by name and direction.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to search |
| `socket_name` | `str` | — | Name of the socket |
| `in_out` | `str` | `"INPUT"` | Socket direction: `"INPUT"` or `"OUTPUT"` |

**Returns:** `bpy.types.NodeTreeInterfaceSocket` or `None`

Searches through `node_tree.interface.items_tree` for a socket matching both the name and direction.

---

#### get_input_socket(node_tree, socket_name)

Get an input socket by name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to search |
| `socket_name` | `str` | — | Name of the socket |

**Returns:** `bpy.types.NodeTreeInterfaceSocket` or `None`

Convenience wrapper for `get_socket()` with `in_out="INPUT"`.

---

#### get_output_socket(node_tree, socket_name)

Get an output socket by name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to search |
| `socket_name` | `str` | — | Name of the socket |

**Returns:** `bpy.types.NodeTreeInterfaceSocket` or `None`

Convenience wrapper for `get_socket()` with `in_out="OUTPUT"`.

---

### Socket Existence Checks

#### has_socket(node_tree, socket_name, in_out="INPUT")

Check if a socket exists.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to search |
| `socket_name` | `str` | — | Name of the socket |
| `in_out` | `str` | `"INPUT"` | Socket direction: `"INPUT"` or `"OUTPUT"` |

**Returns:** `bool` — `True` if the socket exists.

---

#### has_input_socket(node_tree, socket_name)

Check if an input socket exists.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to search |
| `socket_name` | `str` | — | Name of the socket |

**Returns:** `bool` — `True` if the input socket exists.

---

#### has_output_socket(node_tree, socket_name)

Check if an output socket exists.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree to search |
| `socket_name` | `str` | — | Name of the socket |

**Returns:** `bool` — `True` if the output socket exists.

---

### Socket Creation

#### create_socket(node_tree, socket_name, socket_type, in_out="INPUT")

Create a new interface socket.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree |
| `socket_name` | `str` | — | Name for the new socket |
| `socket_type` | `str` | — | Socket type (e.g., `"NodeSocketFloat"`) |
| `in_out` | `str` | `"INPUT"` | Socket direction: `"INPUT"` or `"OUTPUT"` |

**Returns:** `bpy.types.NodeTreeInterfaceSocket` — The newly created socket.

Uses `node_tree.interface.new_socket()` to create the socket with the specified properties.

---

#### create_input_socket(node_tree, socket_name, socket_type)

Create a new input socket.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree |
| `socket_name` | `str` | — | Name for the new socket |
| `socket_type` | `str` | — | Socket type |

**Returns:** `bpy.types.NodeTreeInterfaceSocket` — The newly created input socket.

---

#### create_output_socket(node_tree, socket_name, socket_type)

Create a new output socket.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `node_tree` | `bpy.types.ShaderNodeTree` | — | The node tree |
| `socket_name` | `str` | — | Name for the new socket |
| `socket_type` | `str` | — | Socket type |

**Returns:** `bpy.types.NodeTreeInterfaceSocket` — The newly created output socket.

---

## Examples

### Basic Socket Operations

```python
from mpfb.services.nodetreeservice import NodeTreeService
import bpy

# Get or create a node group
node_tree = bpy.data.node_groups.get("MyNodeGroup")
if not node_tree:
    node_tree = bpy.data.node_groups.new("MyNodeGroup", "ShaderNodeTree")

# Check if a socket exists before creating
if not NodeTreeService.has_input_socket(node_tree, "Factor"):
    socket = NodeTreeService.create_input_socket(
        node_tree, "Factor", "NodeSocketFloat"
    )
    socket.default_value = 0.5
    socket.min_value = 0.0
    socket.max_value = 1.0
```

### Creating a Complete Node Group Interface

```python
from mpfb.services.nodetreeservice import NodeTreeService
import bpy

def setup_skin_shader_interface(node_tree):
    """Set up the interface sockets for a skin shader group."""

    # Input sockets
    inputs = [
        ("Base Color", "NodeSocketColor"),
        ("Roughness", "NodeSocketFloat"),
        ("Subsurface", "NodeSocketFloat"),
        ("Normal", "NodeSocketVector"),
    ]

    for name, socket_type in inputs:
        if not NodeTreeService.has_input_socket(node_tree, name):
            socket = NodeTreeService.create_input_socket(node_tree, name, socket_type)
            # Set defaults for float sockets
            if socket_type == "NodeSocketFloat":
                if name == "Roughness":
                    socket.default_value = 0.5
                elif name == "Subsurface":
                    socket.default_value = 0.1

    # Output sockets
    if not NodeTreeService.has_output_socket(node_tree, "Shader"):
        NodeTreeService.create_output_socket(node_tree, "Shader", "NodeSocketShader")

# Usage
skin_tree = bpy.data.node_groups.new("MPFB_Skin", "ShaderNodeTree")
setup_skin_shader_interface(skin_tree)
```

### Querying Socket Properties

```python
from mpfb.services.nodetreeservice import NodeTreeService

node_tree = bpy.data.node_groups["MyNodeGroup"]

# Get a socket and read its properties
factor_socket = NodeTreeService.get_input_socket(node_tree, "Factor")
if factor_socket:
    print(f"Name: {factor_socket.name}")
    print(f"Type: {factor_socket.socket_type}")
    print(f"Default: {factor_socket.default_value}")
    if hasattr(factor_socket, 'min_value'):
        print(f"Range: {factor_socket.min_value} - {factor_socket.max_value}")
```

### Conditional Socket Creation

```python
from mpfb.services.nodetreeservice import NodeTreeService

def ensure_node_group_has_sockets(node_tree, required_inputs, required_outputs):
    """Ensure a node group has all required sockets."""

    missing_inputs = []
    missing_outputs = []

    for name, socket_type in required_inputs:
        if not NodeTreeService.has_input_socket(node_tree, name):
            NodeTreeService.create_input_socket(node_tree, name, socket_type)
            missing_inputs.append(name)

    for name, socket_type in required_outputs:
        if not NodeTreeService.has_output_socket(node_tree, name):
            NodeTreeService.create_output_socket(node_tree, name, socket_type)
            missing_outputs.append(name)

    if missing_inputs:
        print(f"Created missing inputs: {missing_inputs}")
    if missing_outputs:
        print(f"Created missing outputs: {missing_outputs}")

# Usage
ensure_node_group_has_sockets(
    node_tree,
    required_inputs=[
        ("Color", "NodeSocketColor"),
        ("Strength", "NodeSocketFloat"),
    ],
    required_outputs=[
        ("Result", "NodeSocketColor"),
    ]
)
```

### Iterating Over All Sockets

```python
from mpfb.services.nodetreeservice import NodeTreeService
import bpy

def list_all_sockets(node_tree):
    """List all interface sockets on a node tree."""
    print(f"Sockets for '{node_tree.name}':")

    for item in node_tree.interface.items_tree:
        if isinstance(item, bpy.types.NodeTreeInterfaceSocket):
            direction = "IN" if item.in_out == "INPUT" else "OUT"
            print(f"  [{direction}] {item.name}: {item.socket_type}")

# Usage
for ng in bpy.data.node_groups:
    if ng.name.startswith("MPFB_"):
        list_all_sockets(ng)
```

### Integration with NodeService

```python
from mpfb.services.nodeservice import NodeService
from mpfb.services.nodetreeservice import NodeTreeService
import bpy

# Create a node group with interface
node_tree = bpy.data.node_groups.new("MixGroup", "ShaderNodeTree")

# Set up interface
NodeTreeService.create_input_socket(node_tree, "Color1", "NodeSocketColor")
NodeTreeService.create_input_socket(node_tree, "Color2", "NodeSocketColor")
NodeTreeService.create_input_socket(node_tree, "Factor", "NodeSocketFloat")
NodeTreeService.create_output_socket(node_tree, "Color", "NodeSocketColor")

# Create internal nodes (using NodeService)
input_node = node_tree.nodes.new("NodeGroupInput")
output_node = node_tree.nodes.new("NodeGroupOutput")
mix_node = NodeService.create_node(node_tree, "ShaderNodeMix", xpos=200)
mix_node.data_type = 'RGBA'

# Link internal nodes
node_tree.links.new(input_node.outputs["Color1"], mix_node.inputs["A"])
node_tree.links.new(input_node.outputs["Color2"], mix_node.inputs["B"])
node_tree.links.new(input_node.outputs["Factor"], mix_node.inputs["Factor"])
node_tree.links.new(mix_node.outputs["Result"], output_node.inputs["Color"])
```
