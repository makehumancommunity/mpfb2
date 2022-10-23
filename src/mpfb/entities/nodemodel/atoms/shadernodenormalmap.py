"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "space",
            "sample_value": "TANGENT"
        },
        {
            "allowed_values": [],
            "class": "str",
            "name": "uv_map",
            "sample_value": ""
        }
    ],
    "class": "ShaderNodeNormalMap",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Strength",
            "index": 0,
            "name": "Strength"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 1,
            "name": "Color"
        }
    ],
    "label": "Normal Map",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 0,
            "list_as_argument": false,
            "name": "Normal"
        }
    ]
}"""
def createShaderNodeNormalMap(self, name=None, color=None, label=None, x=None, y=None, space=None, uv_map=None, Strength=None, Color=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeNormalMap"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["space"] = space
    node_def["attributes"]["uv_map"] = uv_map
    node_def["inputs"]["Strength"] = Strength
    node_def["inputs"]["Color"] = Color

    return self._create_node(node_def)
