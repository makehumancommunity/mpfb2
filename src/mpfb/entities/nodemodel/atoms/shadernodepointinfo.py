"""
{
    "attributes": [],
    "class": "ShaderNodePointInfo",
    "inputs": [],
    "label": "Point Info",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Position",
            "index": 0,
            "list_as_argument": false,
            "name": "Position"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Radius",
            "index": 1,
            "list_as_argument": false,
            "name": "Radius"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Random",
            "index": 2,
            "list_as_argument": false,
            "name": "Random"
        }
    ]
}"""
def createShaderNodePointInfo(self, name=None, color=None, label=None, x=None, y=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodePointInfo"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y

    return self._create_node(node_def)
