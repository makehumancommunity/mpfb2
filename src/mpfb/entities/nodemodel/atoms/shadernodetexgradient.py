"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "color_mapping",
            "sample_value": "<bpy_struct, ColorMapping at 0x7f64191b9c98>"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "gradient_type",
            "sample_value": "LINEAR"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "texture_mapping",
            "sample_value": "<bpy_struct, TexMapping at 0x7f64191b9c08>"
        }
    ],
    "class": "ShaderNodeTexGradient",
    "inputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        }
    ],
    "label": "Gradient Texture",
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
def createShaderNodeTexGradient(self, name=None, color=None, label=None, x=None, y=None, color_mapping=None, gradient_type=None, texture_mapping=None, Vector=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeTexGradient"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["color_mapping"] = color_mapping
    node_def["attributes"]["gradient_type"] = gradient_type
    node_def["attributes"]["texture_mapping"] = texture_mapping
    node_def["inputs"]["Vector"] = Vector

    return self._create_node(node_def)
