"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "component",
            "sample_value": "DIFFUSE"
        }
    ],
    "class": "ShaderNodeBsdfToon",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Size",
            "index": 1,
            "name": "Size"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Smooth",
            "index": 2,
            "name": "Smooth"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 3,
            "name": "Normal"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Weight",
            "index": 4,
            "name": "Weight"
        }
    ],
    "label": "Toon BSDF",
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
def createShaderNodeBsdfToon(self, name=None, color=None, label=None, x=None, y=None, component=None, Color=None, Size=None, Smooth=None, Normal=None, Weight=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeBsdfToon"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["component"] = component
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Size"] = Size
    node_def["inputs"]["Smooth"] = Smooth
    node_def["inputs"]["Normal"] = Normal
    node_def["inputs"]["Weight"] = Weight

    return self._create_node(node_def)
