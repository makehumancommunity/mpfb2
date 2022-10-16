"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "bands_direction",
            "sample_value": "X"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "color_mapping",
            "sample_value": "<bpy_struct, ColorMapping at 0x7f64191b9098>"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "rings_direction",
            "sample_value": "X"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "texture_mapping",
            "sample_value": "<bpy_struct, TexMapping at 0x7f64191b9008>"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "wave_profile",
            "sample_value": "SIN"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "wave_type",
            "sample_value": "BANDS"
        }
    ],
    "class": "ShaderNodeTexWave",
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
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Detail",
            "index": 3,
            "name": "Detail"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Detail Scale",
            "index": 4,
            "name": "Detail Scale"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Detail Roughness",
            "index": 5,
            "name": "Detail Roughness"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Phase Offset",
            "index": 6,
            "name": "Phase Offset"
        }
    ],
    "label": "Wave Texture",
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
def createShaderNodeTexWave(self, name=None, color=None, label=None, x=None, y=None, bands_direction=None, color_mapping=None, rings_direction=None, texture_mapping=None, wave_profile=None, wave_type=None, Vector=None, Scale=None, Distortion=None, Detail=None, Detail_Scale=None, Detail_Roughness=None, Phase_Offset=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeTexWave"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["bands_direction"] = bands_direction
    node_def["attributes"]["color_mapping"] = color_mapping
    node_def["attributes"]["rings_direction"] = rings_direction
    node_def["attributes"]["texture_mapping"] = texture_mapping
    node_def["attributes"]["wave_profile"] = wave_profile
    node_def["attributes"]["wave_type"] = wave_type
    node_def["inputs"]["Vector"] = Vector
    node_def["inputs"]["Scale"] = Scale
    node_def["inputs"]["Distortion"] = Distortion
    node_def["inputs"]["Detail"] = Detail
    node_def["inputs"]["Detail Scale"] = Detail_Scale
    node_def["inputs"]["Detail Roughness"] = Detail_Roughness
    node_def["inputs"]["Phase Offset"] = Phase_Offset

    return self._create_node(node_def)
