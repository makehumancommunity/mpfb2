"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "color_mapping",
            "sample_value": "<bpy_struct, ColorMapping at 0x7f641826ac98>"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "noise_dimensions",
            "sample_value": "3D"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "texture_mapping",
            "sample_value": "<bpy_struct, TexMapping at 0x7f641826ac08>"
        }
    ],
    "class": "ShaderNodeTexNoise",
    "inputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "W",
            "index": 1,
            "name": "W"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Scale",
            "index": 2,
            "name": "Scale"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Detail",
            "index": 3,
            "name": "Detail"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Roughness",
            "index": 4,
            "name": "Roughness"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Distortion",
            "index": 5,
            "name": "Distortion"
        }
    ],
    "label": "Noise Texture",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Fac",
            "index": 0,
            "name": "Fac"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 1,
            "name": "Color"
        }
    ]
}"""
def createShaderNodeTexNoise(self, name=None, color=None, label=None, x=None, y=None, color_mapping=None, noise_dimensions=None, texture_mapping=None, Vector=None, W=None, Scale=None, Detail=None, Roughness=None, Distortion=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeTexNoise"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["color_mapping"] = color_mapping
    node_def["attributes"]["noise_dimensions"] = noise_dimensions
    node_def["attributes"]["texture_mapping"] = texture_mapping
    node_def["inputs"]["Vector"] = Vector
    node_def["inputs"]["W"] = W
    node_def["inputs"]["Scale"] = Scale
    node_def["inputs"]["Detail"] = Detail
    node_def["inputs"]["Roughness"] = Roughness
    node_def["inputs"]["Distortion"] = Distortion

    return self._create_node(node_def)
