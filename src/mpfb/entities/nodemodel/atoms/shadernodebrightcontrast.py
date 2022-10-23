"""
{
    "attributes": [],
    "class": "ShaderNodeBrightContrast",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Bright",
            "index": 1,
            "name": "Bright"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Contrast",
            "index": 2,
            "name": "Contrast"
        }
    ],
    "label": "Bright/Contrast",
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
def createShaderNodeBrightContrast(self, name=None, color=None, label=None, x=None, y=None, Color=None, Bright=None, Contrast=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeBrightContrast"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Bright"] = Bright
    node_def["inputs"]["Contrast"] = Contrast

    return self._create_node(node_def)
