"""
{
    "attributes": [],
    "class": "ShaderNodeGamma",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloatUnsigned",
            "identifier": "Gamma",
            "index": 1,
            "name": "Gamma"
        }
    ],
    "label": "Gamma",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "list_as_argument": false,
            "name": "Color"
        }
    ]
}"""
def createShaderNodeGamma(self, name=None, color=None, label=None, x=None, y=None, Color=None, Gamma=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeGamma"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Gamma"] = Gamma

    return self._create_node(node_def)
