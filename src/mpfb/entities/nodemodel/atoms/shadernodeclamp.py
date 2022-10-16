"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "clamp_type",
            "sample_value": "MINMAX"
        }
    ],
    "class": "ShaderNodeClamp",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Value",
            "index": 0,
            "name": "Value"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Min",
            "index": 1,
            "name": "Min"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Max",
            "index": 2,
            "name": "Max"
        }
    ],
    "label": "Clamp",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Result",
            "index": 0,
            "name": "Result"
        }
    ]
}"""
def createShaderNodeClamp(self, name=None, color=None, label=None, x=None, y=None, clamp_type=None, Value=None, Min=None, Max=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeClamp"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["clamp_type"] = clamp_type
    node_def["inputs"]["Value"] = Value
    node_def["inputs"]["Min"] = Min
    node_def["inputs"]["Max"] = Max

    return self._create_node(node_def)
