"""
{
    "attributes": [],
    "class": "ShaderNodeNormal",
    "inputs": [
        {
            "class": "NodeSocketVectorDirection",
            "identifier": "Normal",
            "index": 0,
            "name": "Normal"
        }
    ],
    "label": "Normal",
    "outputs": [
        {
            "class": "NodeSocketVectorDirection",
            "identifier": "Normal",
            "index": 0,
            "name": "Normal"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Dot",
            "index": 1,
            "name": "Dot"
        }
    ]
}"""
def createShaderNodeNormal(self, name=None, color=None, label=None, x=None, y=None, Normal=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeNormal"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Normal"] = Normal

    return self._create_node(node_def)
