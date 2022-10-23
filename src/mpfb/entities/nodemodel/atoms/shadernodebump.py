"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "bool",
            "name": "invert",
            "sample_value": "False"
        }
    ],
    "class": "ShaderNodeBump",
    "inputs": [
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Strength",
            "index": 0,
            "name": "Strength"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Distance",
            "index": 1,
            "name": "Distance"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Height",
            "index": 2,
            "name": "Height"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 3,
            "name": "Normal"
        }
    ],
    "label": "Bump",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 0,
            "list_as_argument": false,
            "name": "Normal"
        }
    ]
}"""
def createShaderNodeBump(self, name=None, color=None, label=None, x=None, y=None, invert=None, Strength=None, Distance=None, Height=None, Normal=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeBump"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["invert"] = invert
    node_def["inputs"]["Strength"] = Strength
    node_def["inputs"]["Distance"] = Distance
    node_def["inputs"]["Height"] = Height
    node_def["inputs"]["Normal"] = Normal

    return self._create_node(node_def)
