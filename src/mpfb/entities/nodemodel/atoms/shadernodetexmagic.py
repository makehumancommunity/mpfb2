"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "color_mapping",
            "sample_value": "<bpy_struct, ColorMapping at 0x7ff28809d498>"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "texture_mapping",
            "sample_value": "<bpy_struct, TexMapping at 0x7ff28809d408>"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "turbulence_depth",
            "sample_value": "2"
        }
    ],
    "class": "ShaderNodeTexMagic",
    "inputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Scale",
            "index": 1,
            "name": "Scale"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Distortion",
            "index": 2,
            "name": "Distortion"
        }
    ],
    "label": "Magic Texture",
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
            "identifier": "Fac",
            "index": 1,
            "list_as_argument": false,
            "name": "Fac"
        }
    ]
}"""
def createShaderNodeTexMagic(self, name=None, color=None, label=None, x=None, y=None, color_mapping=None, texture_mapping=None, turbulence_depth=None, Vector=None, Scale=None, Distortion=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeTexMagic"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["color_mapping"] = color_mapping
    node_def["attributes"]["texture_mapping"] = texture_mapping
    node_def["attributes"]["turbulence_depth"] = turbulence_depth
    node_def["inputs"]["Vector"] = Vector
    node_def["inputs"]["Scale"] = Scale
    node_def["inputs"]["Distortion"] = Distortion

    return self._create_node(node_def)
