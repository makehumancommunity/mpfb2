"""
{
    "attributes": [],
    "class": "ShaderNodeHueSaturation",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Hue",
            "index": 0,
            "name": "Hue"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Saturation",
            "index": 1,
            "name": "Saturation"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Value",
            "index": 2,
            "name": "Value"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Fac",
            "index": 3,
            "name": "Fac"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 4,
            "name": "Color"
        }
    ],
    "label": "Hue Saturation Value",
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
def createShaderNodeHueSaturation(self, name=None, color=None, label=None, x=None, y=None, Hue=None, Saturation=None, Value=None, Fac=None, Color=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeHueSaturation"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Hue"] = Hue
    node_def["inputs"]["Saturation"] = Saturation
    node_def["inputs"]["Value"] = Value
    node_def["inputs"]["Fac"] = Fac
    node_def["inputs"]["Color"] = Color

    return self._create_node(node_def)
