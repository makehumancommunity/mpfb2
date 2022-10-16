"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "operation",
            "sample_value": "ADD"
        },
        {
            "allowed_values": [],
            "class": "bool",
            "name": "use_clamp",
            "sample_value": "False"
        }
    ],
    "class": "ShaderNodeMath",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Value",
            "index": 0,
            "name": "Value"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Value_001",
            "index": 1,
            "name": "Value"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Value_002",
            "index": 2,
            "name": "Value"
        }
    ],
    "label": "Math",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Value",
            "index": 0,
            "name": "Value"
        }
    ]
}"""
def createShaderNodeMath(self, name=None, color=None, label=None, x=None, y=None, operation=None, use_clamp=None, Value=None, Value_001=None, Value_002=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeMath"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["operation"] = operation
    node_def["attributes"]["use_clamp"] = use_clamp
    node_def["inputs"]["Value"] = Value
    node_def["inputs"]["Value_001"] = Value_001
    node_def["inputs"]["Value_002"] = Value_002

    return self._create_node(node_def)
