"""
{
    "attributes": [],
    "class": "ShaderNodeVolumeScatter",
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
            "class": "NodeSocketFloatFactor",
            "identifier": "Anisotropy",
            "index": 2,
            "name": "Anisotropy"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Weight",
            "index": 3,
            "name": "Weight"
        }
    ],
    "label": "Volume Scatter",
    "outputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "Volume",
            "index": 0,
            "name": "Volume"
        }
    ]
}"""
def createShaderNodeVolumeScatter(self, name=None, color=None, label=None, x=None, y=None, Color=None, Density=None, Anisotropy=None, Weight=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeVolumeScatter"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Density"] = Density
    node_def["inputs"]["Anisotropy"] = Anisotropy
    node_def["inputs"]["Weight"] = Weight

    return self._create_node(node_def)
