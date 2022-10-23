"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "str",
            "name": "layer_name",
            "sample_value": ""
        }
    ],
    "class": "ShaderNodeVertexColor",
    "inputs": [],
    "label": "Color Attribute",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "list_as_argument": false,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Alpha",
            "index": 1,
            "list_as_argument": false,
            "name": "Alpha"
        }
    ]
}"""
def createShaderNodeVertexColor(self, name=None, color=None, label=None, x=None, y=None, layer_name=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeVertexColor"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["layer_name"] = layer_name

    return self._create_node(node_def)
