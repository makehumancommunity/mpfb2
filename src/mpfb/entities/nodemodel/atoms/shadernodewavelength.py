"""
{
    "attributes": [],
    "class": "ShaderNodeWavelength",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Wavelength",
            "index": 0,
            "name": "Wavelength"
        }
    ],
    "label": "Wavelength",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        }
    ]
}"""
def createShaderNodeWavelength(self, name=None, color=None, label=None, x=None, y=None, Wavelength=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeWavelength"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["Wavelength"] = Wavelength

    return self._create_node(node_def)
