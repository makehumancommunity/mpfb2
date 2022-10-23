"""
{
    "attributes": [],
    "class": "ShaderNodeBsdfTransparent",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Weight",
            "index": 1,
            "name": "Weight"
        }
    ],
    "label": "Transparent BSDF",
    "outputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "BSDF",
            "index": 0,
            "list_as_argument": false,
            "name": "BSDF"
        }
    ]
}"""
def createShaderNodeBsdfTransparent(self, name=None, color=None, label=None, x=None, y=None, Color=None, Weight=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeBsdfTransparent"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Weight"] = Weight

    return self._create_node(node_def)
