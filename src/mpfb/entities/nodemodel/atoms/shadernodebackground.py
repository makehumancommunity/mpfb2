"""
{
    "attributes": [],
    "class": "ShaderNodeBackground",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Strength",
            "index": 1,
            "name": "Strength"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Weight",
            "index": 2,
            "name": "Weight"
        }
    ],
    "label": "Background",
    "outputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "Background",
            "index": 0,
            "name": "Background"
        }
    ]
}"""
def createShaderNodeBackground(self, name=None, color=None, label=None, x=None, y=None, Color=None, Strength=None, Weight=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeBackground"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Strength"] = Strength
    node_def["inputs"]["Weight"] = Weight

    return self._create_node(node_def)
