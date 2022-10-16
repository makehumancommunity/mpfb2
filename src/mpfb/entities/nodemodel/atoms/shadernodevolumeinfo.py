"""
{
    "attributes": [],
    "class": "ShaderNodeVolumeInfo",
    "inputs": [],
    "label": "Volume Info",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Density",
            "index": 1,
            "name": "Density"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Flame",
            "index": 2,
            "name": "Flame"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Temperature",
            "index": 3,
            "name": "Temperature"
        }
    ]
}"""
def createShaderNodeVolumeInfo(self, name=None, color=None, label=None, x=None, y=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeVolumeInfo"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y

    return self._create_node(node_def)
