"""
{
    "attributes": [],
    "class": "ShaderNodeShaderToRGB",
    "inputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "Shader",
            "index": 0,
            "name": "Shader"
        }
    ],
    "label": "Shader to RGB",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "list_as_argument": false,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Alpha",
            "index": 1,
            "list_as_argument": false,
            "name": "Alpha"
        }
    ]
}"""
def createShaderNodeShaderToRGB(self, name=None, color=None, label=None, x=None, y=None, Shader=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeShaderToRGB"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Shader"] = Shader

    return self._create_node(node_def)
