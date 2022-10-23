"""
{
    "attributes": [],
    "class": "ShaderNodeValue",
    "inputs": [],
    "label": "Value",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Value",
            "index": 0,
            "list_as_argument": true,
            "name": "Value"
        }
    ]
}"""
def createShaderNodeValue(self, name=None, color=None, label=None, x=None, y=None, Value=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeValue"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["outputs"]["Value"] = Value

    return self._create_node(node_def)
