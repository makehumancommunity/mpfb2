"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "bool",
            "name": "invert",
            "sample_value": "False"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "rotation_type",
            "sample_value": "AXIS_ANGLE"
        }
    ],
    "class": "ShaderNodeVectorRotate",
    "inputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Center",
            "index": 1,
            "name": "Center"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Axis",
            "index": 2,
            "name": "Axis"
        },
        {
            "class": "NodeSocketFloatAngle",
            "identifier": "Angle",
            "index": 3,
            "name": "Angle"
        },
        {
            "class": "NodeSocketVectorEuler",
            "identifier": "Rotation",
            "index": 4,
            "name": "Rotation"
        }
    ],
    "label": "Vector Rotate",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        }
    ]
}"""
def createShaderNodeVectorRotate(self, name=None, color=None, label=None, x=None, y=None, invert=None, rotation_type=None, Vector=None, Center=None, Axis=None, Angle=None, Rotation=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeVectorRotate"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["invert"] = invert
    node_def["attributes"]["rotation_type"] = rotation_type
    node_def["inputs"]["Vector"] = Vector
    node_def["inputs"]["Center"] = Center
    node_def["inputs"]["Axis"] = Axis
    node_def["inputs"]["Angle"] = Angle
    node_def["inputs"]["Rotation"] = Rotation

    return self._create_node(node_def)
