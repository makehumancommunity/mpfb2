"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "space",
            "sample_value": "OBJECT"
        }
    ],
    "class": "ShaderNodeDisplacement",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Height",
            "index": 0,
            "name": "Height"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Midlevel",
            "index": 1,
            "name": "Midlevel"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Scale",
            "index": 2,
            "name": "Scale"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 3,
            "name": "Normal"
        }
    ],
    "label": "Displacement",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Displacement",
            "index": 0,
            "list_as_argument": false,
            "name": "Displacement"
        }
    ]
}"""
def createShaderNodeDisplacement(self, name=None, color=None, label=None, x=None, y=None, space=None, Height=None, Midlevel=None, Scale=None, Normal=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeDisplacement"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["space"] = space
    node_def["inputs"]["Height"] = Height
    node_def["inputs"]["Midlevel"] = Midlevel
    node_def["inputs"]["Scale"] = Scale
    node_def["inputs"]["Normal"] = Normal

    return self._create_node(node_def)
