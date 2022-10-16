"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "blend_type",
            "sample_value": "MIX"
        },
        {
            "allowed_values": [],
            "class": "bool",
            "name": "use_alpha",
            "sample_value": "False"
        },
        {
            "allowed_values": [],
            "class": "bool",
            "name": "use_clamp",
            "sample_value": "False"
        }
    ],
    "class": "ShaderNodeMixRGB",
    "inputs": [
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Fac",
            "index": 0,
            "name": "Fac"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Color1",
            "index": 1,
            "name": "Color1"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Color2",
            "index": 2,
            "name": "Color2"
        }
    ],
    "label": "Mix",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        }
    ]
}"""
def createShaderNodeMixRGB(self, name=None, color=None, label=None, x=None, y=None, blend_type=None, use_alpha=None, use_clamp=None, Fac=None, Color1=None, Color2=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeMixRGB"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["blend_type"] = blend_type
    node_def["attributes"]["use_alpha"] = use_alpha
    node_def["attributes"]["use_clamp"] = use_clamp
    node_def["inputs"]["Fac"] = Fac
    node_def["inputs"]["Color1"] = Color1
    node_def["inputs"]["Color2"] = Color2

    return self._create_node(node_def)
