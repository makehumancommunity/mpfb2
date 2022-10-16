"""
{
    "attributes": [],
    "class": "ShaderNodeRGBToBW",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        }
    ],
    "label": "RGB to BW",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Val",
            "index": 0,
            "name": "Val"
        }
    ]
}"""
def createShaderNodeRGBToBW(self, name=None, color=None, label=None, x=None, y=None, Color=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeRGBToBW"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Color"] = Color

    return self._create_node(node_def)
