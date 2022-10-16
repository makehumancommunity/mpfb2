"""
{
    "attributes": [],
    "class": "ShaderNodeInvert",
    "inputs": [
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Fac",
            "index": 0,
            "name": "Fac"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 1,
            "name": "Color"
        }
    ],
    "label": "Invert",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        }
    ]
}"""
def createShaderNodeInvert(self, name=None, color=None, label=None, x=None, y=None, Fac=None, Color=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeInvert"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Fac"] = Fac
    node_def["inputs"]["Color"] = Color

    return self._create_node(node_def)
