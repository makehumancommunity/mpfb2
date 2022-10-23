"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "space",
            "sample_value": "TANGENT"
        }
    ],
    "class": "ShaderNodeVectorDisplacement",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
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
        }
    ],
    "label": "Vector Displacement",
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
def createShaderNodeVectorDisplacement(self, name=None, color=None, label=None, x=None, y=None, space=None, Vector=None, Midlevel=None, Scale=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeVectorDisplacement"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["space"] = space
    node_def["inputs"]["Vector"] = Vector
    node_def["inputs"]["Midlevel"] = Midlevel
    node_def["inputs"]["Scale"] = Scale

    return self._create_node(node_def)
