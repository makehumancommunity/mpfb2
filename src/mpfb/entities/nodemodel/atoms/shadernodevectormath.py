"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "operation",
            "sample_value": "ADD"
        }
    ],
    "class": "ShaderNodeVectorMath",
    "inputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Vector_001",
            "index": 1,
            "name": "Vector"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Vector_002",
            "index": 2,
            "name": "Vector"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Scale",
            "index": 3,
            "name": "Scale"
        }
    ],
    "label": "Vector Math",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Value",
            "index": 1,
            "name": "Value"
        }
    ]
}"""
def createShaderNodeVectorMath(self, name=None, color=None, label=None, x=None, y=None, operation=None, Vector=None, Vector_001=None, Vector_002=None, Scale=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeVectorMath"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["operation"] = operation
    node_def["inputs"]["Vector"] = Vector
    node_def["inputs"]["Vector_001"] = Vector_001
    node_def["inputs"]["Vector_002"] = Vector_002
    node_def["inputs"]["Scale"] = Scale

    return self._create_node(node_def)
