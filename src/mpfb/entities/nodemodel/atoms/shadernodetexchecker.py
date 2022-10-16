"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "color_mapping",
            "sample_value": "<bpy_struct, ColorMapping at 0x7f64191bd498>"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "texture_mapping",
            "sample_value": "<bpy_struct, TexMapping at 0x7f64191bd408>"
        }
    ],
    "class": "ShaderNodeTexChecker",
    "inputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
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
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Scale",
            "index": 3,
            "name": "Scale"
        }
    ],
    "label": "Checker Texture",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Fac",
            "index": 1,
            "name": "Fac"
        }
    ]
}"""
def createShaderNodeTexChecker(self, name=None, color=None, label=None, x=None, y=None, color_mapping=None, texture_mapping=None, Vector=None, Color1=None, Color2=None, Scale=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeTexChecker"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["color_mapping"] = color_mapping
    node_def["attributes"]["texture_mapping"] = texture_mapping
    node_def["inputs"]["Vector"] = Vector
    node_def["inputs"]["Color1"] = Color1
    node_def["inputs"]["Color2"] = Color2
    node_def["inputs"]["Scale"] = Scale

    return self._create_node(node_def)
