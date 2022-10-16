"""
{
    "attributes": [],
    "class": "ShaderNodeVolumeAbsorption",
    "inputs": [
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
            "identifier": "Weight",
            "index": 2,
            "name": "Weight"
        }
    ],
    "label": "Volume Absorption",
    "outputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "Volume",
            "index": 0,
            "name": "Volume"
        }
    ]
}"""
def createShaderNodeVolumeAbsorption(self, name=None, color=None, label=None, x=None, y=None, Color=None, Density=None, Weight=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeVolumeAbsorption"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Density"] = Density
    node_def["inputs"]["Weight"] = Weight

    return self._create_node(node_def)
