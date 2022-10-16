"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "mapping",
            "sample_value": "<bpy_struct, CurveMapping at 0x7f6418c75388>"
        }
    ],
    "class": "ShaderNodeFloatCurve",
    "inputs": [
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Factor",
            "index": 0,
            "name": "Factor"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Value",
            "index": 1,
            "name": "Value"
        }
    ],
    "label": "Float Curve",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Value",
            "index": 0,
            "name": "Value"
        }
    ]
}"""
def createShaderNodeFloatCurve(self, name=None, color=None, label=None, x=None, y=None, mapping=None, Factor=None, Value=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeFloatCurve"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["mapping"] = mapping
    node_def["inputs"]["Factor"] = Factor
    node_def["inputs"]["Value"] = Value

    return self._create_node(node_def)
