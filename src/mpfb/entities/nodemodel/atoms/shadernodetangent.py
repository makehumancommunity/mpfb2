"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "axis",
            "sample_value": "Z"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "direction_type",
            "sample_value": "RADIAL"
        },
        {
            "allowed_values": [],
            "class": "str",
            "name": "uv_map",
            "sample_value": ""
        }
    ],
    "class": "ShaderNodeTangent",
    "inputs": [],
    "label": "Tangent",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Tangent",
            "index": 0,
            "list_as_argument": false,
            "name": "Tangent"
        }
    ]
}"""
def createShaderNodeTangent(self, name=None, color=None, label=None, x=None, y=None, axis=None, direction_type=None, uv_map=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeTangent"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["axis"] = axis
    node_def["attributes"]["direction_type"] = direction_type
    node_def["attributes"]["uv_map"] = uv_map

    return self._create_node(node_def)
