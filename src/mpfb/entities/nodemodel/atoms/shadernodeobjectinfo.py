"""
{
    "attributes": [],
    "class": "ShaderNodeObjectInfo",
    "inputs": [],
    "label": "Object Info",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Location",
            "index": 0,
            "name": "Location"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 1,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Alpha",
            "index": 2,
            "name": "Alpha"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Object Index",
            "index": 3,
            "name": "Object Index"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Material Index",
            "index": 4,
            "name": "Material Index"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Random",
            "index": 5,
            "name": "Random"
        }
    ]
}"""
def createShaderNodeObjectInfo(self, name=None, color=None, label=None, x=None, y=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeObjectInfo"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y

    return self._create_node(node_def)
