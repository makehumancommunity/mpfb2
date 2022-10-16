"""
{
    "attributes": [],
    "class": "ShaderNodeSeparateXYZ",
    "inputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        }
    ],
    "label": "Separate XYZ",
    "outputs": [
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
    ]
}"""
def createShaderNodeSeparateXYZ(self, name=None, color=None, label=None, x=None, y=None, Vector=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeSeparateXYZ"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Vector"] = Vector

    return self._create_node(node_def)
