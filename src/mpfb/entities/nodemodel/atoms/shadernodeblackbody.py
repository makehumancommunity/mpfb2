"""
{
    "attributes": [],
    "class": "ShaderNodeBlackbody",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Temperature",
            "index": 0,
            "name": "Temperature"
        }
    ],
    "label": "Blackbody",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        }
    ]
}"""
def createShaderNodeBlackbody(self, name=None, color=None, label=None, x=None, y=None, Temperature=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeBlackbody"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Temperature"] = Temperature

    return self._create_node(node_def)
