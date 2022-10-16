"""
{
    "attributes": [],
    "class": "ShaderNodeBsdfVelvet",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Sigma",
            "index": 1,
            "name": "Sigma"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 2,
            "name": "Normal"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Weight",
            "index": 3,
            "name": "Weight"
        }
    ],
    "label": "Velvet BSDF",
    "outputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "BSDF",
            "index": 0,
            "name": "BSDF"
        }
    ]
}"""
def createShaderNodeBsdfVelvet(self, name=None, color=None, label=None, x=None, y=None, Color=None, Sigma=None, Normal=None, Weight=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeBsdfVelvet"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Sigma"] = Sigma
    node_def["inputs"]["Normal"] = Normal
    node_def["inputs"]["Weight"] = Weight

    return self._create_node(node_def)
