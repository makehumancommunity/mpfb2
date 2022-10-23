"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "vector_type",
            "sample_value": "POINT"
        }
    ],
    "class": "ShaderNodeMapping",
    "inputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        },
        {
            "class": "NodeSocketVectorTranslation",
            "identifier": "Location",
            "index": 1,
            "name": "Location"
        },
        {
            "class": "NodeSocketVectorEuler",
            "identifier": "Rotation",
            "index": 2,
            "name": "Rotation"
        },
        {
            "class": "NodeSocketVectorXYZ",
            "identifier": "Scale",
            "index": 3,
            "name": "Scale"
        }
    ],
    "label": "Mapping",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "list_as_argument": false,
            "name": "Vector"
        }
    ]
}"""
def createShaderNodeMapping(self, name=None, color=None, label=None, x=None, y=None, vector_type=None, Vector=None, Location=None, Rotation=None, Scale=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeMapping"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["vector_type"] = vector_type
    node_def["inputs"]["Vector"] = Vector
    node_def["inputs"]["Location"] = Location
    node_def["inputs"]["Rotation"] = Rotation
    node_def["inputs"]["Scale"] = Scale

    return self._create_node(node_def)
