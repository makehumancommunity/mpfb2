"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "str",
            "name": "filepath",
            "sample_value": ""
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "ies",
            "sample_value": "None"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "mode",
            "sample_value": "INTERNAL"
        }
    ],
    "class": "ShaderNodeTexIES",
    "inputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Strength",
            "index": 1,
            "name": "Strength"
        }
    ],
    "label": "IES Texture",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Fac",
            "index": 0,
            "name": "Fac"
        }
    ]
}"""
def createShaderNodeTexIES(self, name=None, color=None, label=None, x=None, y=None, filepath=None, ies=None, mode=None, Vector=None, Strength=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeTexIES"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["filepath"] = filepath
    node_def["attributes"]["ies"] = ies
    node_def["attributes"]["mode"] = mode
    node_def["inputs"]["Vector"] = Vector
    node_def["inputs"]["Strength"] = Strength

    return self._create_node(node_def)
