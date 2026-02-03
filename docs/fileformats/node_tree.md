# Node Tree / Shader Definition

This file explains the node tree JSON format used by MPFB to define Blender shader networks.

## Purpose

A node tree file defines a complete Blender shader node network as JSON. This allows MPFB to create
procedural materials (enhanced skin, procedural eyes, MakeSkin materials) from templates with conditional
nodes and variable substitution. Node tree files are located in `src/mpfb/data/node_trees/`.

In most cases, these files are not written by hand. There is some tooling available in the shader
node view in blender, although the UX leaves a bit to be desired.

## Structure

A node tree file is a JSON object with nested group definitions. The format supports variable substitution
via `$variable` placeholders that are resolved at runtime. Files are parsed by
`NodeService.apply_node_tree_from_dict()` in `src/mpfb/services/nodeservice.py`.

### Top-level keys

- `groups` (object, required) — Dictionary of node group definitions. Each key is a group name (may contain `$` placeholders).

### Group definition

Each group in the `groups` object has these keys:

- `groups` (object) — Nested sub-group definitions (same structure, recursive).
- `inputs` (object) — Input sockets for the group interface.
- `outputs` (object) — Output sockets for the group interface.
- `nodes` (object) — Nodes contained in this group.
- `links` (array) — Connections between nodes.

### Input sockets

Each key in `inputs` is a socket name. The value is an object:

- `type` (string, required) — Blender socket type, e.g. `"NodeSocketFloat"`, `"NodeSocketColor"`, `"NodeSocketVector"`, `"NodeSocketShader"`.
- `value` (varies, optional) — Default value. Floats for numeric sockets, 4-element RGBA arrays for colors. Can be a `$variable` placeholder.
- `create` (boolean or string, optional) — Whether to create this socket. Can be `true`, `false`, or a `$variable` placeholder for conditional creation.
- `min_value` (float, optional) — Minimum value for numeric sockets.
- `max_value` (float, optional) — Maximum value for numeric sockets.

### Output sockets

Each key in `outputs` is a socket name. The value is a string specifying the Blender socket type (e.g. `"NodeSocketShader"`).

### Nodes

Each key in `nodes` is a node name. The value is an object:

- `name` (string, required) — Node identifier.
- `type` (string, required) — Blender node type, e.g. `"ShaderNodeBsdfPrincipled"`, `"ShaderNodeTexImage"`, `"ShaderNodeMath"`, `"ShaderNodeGroup"`.
- `label` (string, optional) — Display label in the node editor.
- `location` (array of 2 floats, required) — `[x, y]` position in the node editor.
- `create` (boolean or string, optional) — Whether to create this node. Can be `true`, `false`, or a `$variable` for conditional creation.
- `values` (object, optional) — Default values for input sockets, keyed by socket name. Values can be floats, arrays, or `$variable` placeholders.
- `operation` (string, optional) — For `ShaderNodeMath` / `ShaderNodeVectorMath`: the operation type (e.g. `"MULTIPLY"`, `"ADD"`).
- `use_clamp` (boolean, optional) — For `ShaderNodeMath`: whether to clamp the output.
- `blend_type` (string, optional) — For `ShaderNodeMix`: blend mode (e.g. `"MIX"`).
- `filename` (string, optional) — For `ShaderNodeTexImage`: image file path. Can be a `$variable`.
- `colorspace` (string, optional) — For `ShaderNodeTexImage`: color space (`"sRGB"`, `"Non-Color"`).
- `value` (float, optional) — For `ShaderNodeValue`: the single output value.
- `stops` (array of floats, optional) — For `ShaderNodeValToRGB`: color ramp stop positions.
- `group_name` (string, optional) — For `ShaderNodeGroup`: which node group to reference.

Special node types `"NodeGroupInput"` and `"NodeGroupOutput"` represent the group's input/output interfaces.

### Links

Each element in the `links` array is an object:

- `from_node` (string, required) — Source node name.
- `from_socket` (string or integer, required) — Output socket name or index.
- `to_node` (string, required) — Target node name.
- `to_socket` (string or integer, required) — Input socket name or index.
- `disabled` (boolean or string, optional) — If `true` or if a `$variable` resolves to `true`, the link is not created.

Socket indices (integers) are used when a node has multiple sockets with the same name.

### Variable substitution

Keys and values containing `$` prefixed names are replaced before JSON parsing:

1. Material code builds a dictionary mapping variable names to values (e.g. `has_sss` -> `"true"`, `diffuse_filename` -> `"/path/to/file.png"`).
2. All occurrences of `"$variable_name"` in the JSON text are replaced with the corresponding value.
3. The resulting valid JSON is then parsed and applied.

Variable types:

- **Boolean** — Controls `create` and `disabled` fields. `"true"` or `"false"`.
- **File path** — Provides texture paths for `filename` fields.
- **Color** — Provides RGBA arrays for `value` fields, e.g. `"[0.5, 0.5, 0.5, 1.0]"`.
- **Numeric** — Provides float values for socket defaults.
- **Group name** — The special `$group_name` placeholder in group keys is replaced with the actual group name.

## Example content

```json
{
  "groups": {
    "$group_name": {
      "inputs": {
        "Base Color": {
          "type": "NodeSocketColor",
          "value": "$diffuseColor"
        },
        "Roughness": {
          "type": "NodeSocketFloat",
          "value": "$Roughness",
          "min_value": 0.0,
          "max_value": 1.0
        },
        "SSS Strength": {
          "type": "NodeSocketFloat",
          "value": 0.1,
          "create": "$has_sss"
        }
      },
      "outputs": {
        "Shader": "NodeSocketShader"
      },
      "nodes": {
        "Group Input": {
          "name": "Group Input",
          "type": "NodeGroupInput",
          "label": "",
          "location": [0, 0],
          "create": true,
          "values": {}
        },
        "Principled BSDF": {
          "name": "Principled BSDF",
          "type": "ShaderNodeBsdfPrincipled",
          "label": "",
          "location": [300, 0],
          "create": true,
          "values": {
            "Metallic": 0.0
          }
        },
        "diffuseTexture": {
          "name": "diffuseTexture",
          "type": "ShaderNodeTexImage",
          "label": "Diffuse",
          "location": [0, -200],
          "create": "$has_diffuse",
          "filename": "$diffuse_filename",
          "colorspace": "sRGB",
          "values": {}
        },
        "Group Output": {
          "name": "Group Output",
          "type": "NodeGroupOutput",
          "label": "",
          "location": [600, 0],
          "create": true,
          "values": {}
        }
      },
      "links": [
        {
          "from_node": "Group Input",
          "from_socket": "Base Color",
          "to_node": "Principled BSDF",
          "to_socket": "Base Color"
        },
        {
          "from_node": "diffuseTexture",
          "from_socket": "Color",
          "to_node": "Principled BSDF",
          "to_socket": "Base Color",
          "disabled": "$has_aomap"
        },
        {
          "from_node": "Principled BSDF",
          "from_socket": "BSDF",
          "to_node": "Group Output",
          "to_socket": "Shader"
        }
      ],
      "groups": {}
    }
  }
}
```
