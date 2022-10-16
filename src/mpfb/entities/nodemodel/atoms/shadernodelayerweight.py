"""
{
    "attributes": [],
    "class": "ShaderNodeLayerWeight",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Blend",
            "index": 0,
            "name": "Blend"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 1,
            "name": "Normal"
        }
    ],
    "label": "Layer Weight",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Fresnel",
            "index": 0,
            "name": "Fresnel"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Facing",
            "index": 1,
            "name": "Facing"
        }
    ]
}"""
def createShaderNodeLayerWeight(self, name=None, color=None, label=None, x=None, y=None, Blend=None, Normal=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeLayerWeight"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Blend"] = Blend
    node_def["inputs"]["Normal"] = Normal

    return self._create_node(node_def)
