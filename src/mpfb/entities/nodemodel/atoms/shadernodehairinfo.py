"""
{
    "attributes": [],
    "class": "ShaderNodeHairInfo",
    "inputs": [],
    "label": "Curves Info",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Is Strand",
            "index": 0,
            "name": "Is Strand"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Intercept",
            "index": 1,
            "name": "Intercept"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Length",
            "index": 2,
            "name": "Length"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Thickness",
            "index": 3,
            "name": "Thickness"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Tangent Normal",
            "index": 4,
            "name": "Tangent Normal"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Random",
            "index": 5,
            "name": "Random"
        }
    ]
}"""
def createShaderNodeHairInfo(self, name=None, color=None, label=None, x=None, y=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeHairInfo"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y

    return self._create_node(node_def)
