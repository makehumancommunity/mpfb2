"""
{
    "attributes": [],
    "class": "ShaderNodeCombineXYZ",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "X",
            "index": 0,
            "name": "X"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Y",
            "index": 1,
            "name": "Y"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Z",
            "index": 2,
            "name": "Z"
        }
    ],
    "label": "Combine XYZ",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "list_as_argument": false,
            "name": "Vector"
        }
    ]
}"""
def createShaderNodeCombineXYZ(self, name=None, color=None, label=None, x=None, y=None, X=None, Y=None, Z=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeCombineXYZ"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["X"] = X
    node_def["inputs"]["Y"] = Y
    node_def["inputs"]["Z"] = Z

    return self._create_node(node_def)
