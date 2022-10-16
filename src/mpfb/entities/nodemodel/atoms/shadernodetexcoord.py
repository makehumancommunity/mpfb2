"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "bool",
            "name": "from_instancer",
            "sample_value": "False"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "object",
            "sample_value": "None"
        }
    ],
    "class": "ShaderNodeTexCoord",
    "inputs": [],
    "label": "Texture Coordinate",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Generated",
            "index": 0,
            "name": "Generated"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 1,
            "name": "Normal"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "UV",
            "index": 2,
            "name": "UV"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Object",
            "index": 3,
            "name": "Object"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Camera",
            "index": 4,
            "name": "Camera"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Window",
            "index": 5,
            "name": "Window"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Reflection",
            "index": 6,
            "name": "Reflection"
        }
    ]
}"""
def createShaderNodeTexCoord(self, name=None, color=None, label=None, x=None, y=None, from_instancer=None, object=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeTexCoord"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["from_instancer"] = from_instancer
    node_def["attributes"]["object"] = object

    return self._create_node(node_def)
