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
            "name": "is_active_output",
            "sample_value": "False"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "target",
            "sample_value": "ALL"
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
    "class": "ShaderNodeOutputLineStyle",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Color Fac",
            "index": 1,
            "name": "Color Fac"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Alpha",
            "index": 2,
            "name": "Alpha"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Alpha Fac",
            "index": 3,
            "name": "Alpha Fac"
        }
    ],
    "label": "Line Style Output",
    "outputs": []
}"""
def createShaderNodeOutputLineStyle(self, name=None, color=None, label=None, x=None, y=None, blend_type=None, is_active_output=None, target=None, use_alpha=None, use_clamp=None, Color=None, Color_Fac=None, Alpha=None, Alpha_Fac=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeOutputLineStyle"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["blend_type"] = blend_type
    node_def["attributes"]["is_active_output"] = is_active_output
    node_def["attributes"]["target"] = target
    node_def["attributes"]["use_alpha"] = use_alpha
    node_def["attributes"]["use_clamp"] = use_clamp
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Color Fac"] = Color_Fac
    node_def["inputs"]["Alpha"] = Alpha
    node_def["inputs"]["Alpha Fac"] = Alpha_Fac

    return self._create_node(node_def)
