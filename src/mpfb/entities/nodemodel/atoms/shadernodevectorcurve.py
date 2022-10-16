"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "mapping",
            "sample_value": "<bpy_struct, CurveMapping at 0x7f6416b94408>"
        }
    ],
    "class": "ShaderNodeVectorCurve",
    "inputs": [
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Fac",
            "index": 0,
            "name": "Fac"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 1,
            "name": "Vector"
        }
    ],
    "label": "Vector Curves",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        }
    ]
}"""
def createShaderNodeVectorCurve(self, name=None, color=None, label=None, x=None, y=None, mapping=None, Fac=None, Vector=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeVectorCurve"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["mapping"] = mapping
    node_def["inputs"]["Fac"] = Fac
    node_def["inputs"]["Vector"] = Vector

    return self._create_node(node_def)
