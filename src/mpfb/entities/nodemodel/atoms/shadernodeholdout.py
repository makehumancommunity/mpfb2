"""
{
    "attributes": [],
    "class": "ShaderNodeHoldout",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Weight",
            "index": 0,
            "name": "Weight"
        }
    ],
    "label": "Holdout",
    "outputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "Holdout",
            "index": 0,
            "name": "Holdout"
        }
    ]
}"""
def createShaderNodeHoldout(self, name=None, color=None, label=None, x=None, y=None, Weight=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeHoldout"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Weight"] = Weight

    return self._create_node(node_def)
