"""
{
    "attributes": [],
    "class": "ShaderNodeOutputAOV",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Value",
            "index": 1,
            "name": "Value"
        }
    ],
    "label": "",
    "outputs": []
}"""
def createShaderNodeOutputAOV(self, name=None, color=None, label=None, x=None, y=None, Color=None, Value=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeOutputAOV"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Value"] = Value

    return self._create_node(node_def)
