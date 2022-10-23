"""
{
    "attributes": [],
    "class": "ShaderNodeLightFalloff",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Strength",
            "index": 0,
            "name": "Strength"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Smooth",
            "index": 1,
            "name": "Smooth"
        }
    ],
    "label": "Light Falloff",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Quadratic",
            "index": 0,
            "list_as_argument": false,
            "name": "Quadratic"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Linear",
            "index": 1,
            "list_as_argument": false,
            "name": "Linear"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Constant",
            "index": 2,
            "list_as_argument": false,
            "name": "Constant"
        }
    ]
}"""
def createShaderNodeLightFalloff(self, name=None, color=None, label=None, x=None, y=None, Strength=None, Smooth=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeLightFalloff"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Strength"] = Strength
    node_def["inputs"]["Smooth"] = Smooth

    return self._create_node(node_def)
