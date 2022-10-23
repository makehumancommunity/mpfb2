"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "bool",
            "name": "use_tips",
            "sample_value": "False"
        }
    ],
    "class": "ShaderNodeUVAlongStroke",
    "inputs": [],
    "label": "UV Along Stroke",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "UV",
            "index": 0,
            "list_as_argument": false,
            "name": "UV"
        }
    ]
}"""
def createShaderNodeUVAlongStroke(self, name=None, color=None, label=None, x=None, y=None, use_tips=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeUVAlongStroke"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["use_tips"] = use_tips

    return self._create_node(node_def)
