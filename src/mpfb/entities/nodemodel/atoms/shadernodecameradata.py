"""
{
    "attributes": [],
    "class": "ShaderNodeCameraData",
    "inputs": [],
    "label": "Camera Data",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "View Vector",
            "index": 0,
            "name": "View Vector"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "View Z Depth",
            "index": 1,
            "name": "View Z Depth"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "View Distance",
            "index": 2,
            "name": "View Distance"
        }
    ]
}"""
def createShaderNodeCameraData(self, name=None, color=None, label=None, x=None, y=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeCameraData"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y

    return self._create_node(node_def)
