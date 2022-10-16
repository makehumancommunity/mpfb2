"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "color_mapping",
            "sample_value": "<bpy_struct, ColorMapping at 0x7f641826a898>"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "image",
            "sample_value": "None"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "image_user",
            "sample_value": "<bpy_struct, ImageUser at 0x7f641826abc8>"
        },
        {
            "allowed_values": [],
            "class": "str",
            "name": "interpolation",
            "sample_value": "Linear"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "projection",
            "sample_value": "EQUIRECTANGULAR"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "texture_mapping",
            "sample_value": "<bpy_struct, TexMapping at 0x7f641826a808>"
        }
    ],
    "class": "ShaderNodeTexEnvironment",
    "inputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        }
    ],
    "label": "Environment Texture",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        }
    ]
}"""
def createShaderNodeTexEnvironment(self, name=None, color=None, label=None, x=None, y=None, color_mapping=None, image=None, image_user=None, interpolation=None, projection=None, texture_mapping=None, Vector=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeTexEnvironment"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["color_mapping"] = color_mapping
    node_def["attributes"]["image"] = image
    node_def["attributes"]["image_user"] = image_user
    node_def["attributes"]["interpolation"] = interpolation
    node_def["attributes"]["projection"] = projection
    node_def["attributes"]["texture_mapping"] = texture_mapping
    node_def["inputs"]["Vector"] = Vector

    return self._create_node(node_def)
