"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "color_mapping",
            "sample_value": "<bpy_struct, ColorMapping at 0x7f64191bd898>"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "offset",
            "sample_value": "0.5"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "offset_frequency",
            "sample_value": "2"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "squash",
            "sample_value": "1.0"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "squash_frequency",
            "sample_value": "2"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "texture_mapping",
            "sample_value": "<bpy_struct, TexMapping at 0x7f64191bd808>"
        }
    ],
    "class": "ShaderNodeTexBrick",
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
            "class": "NodeSocketColor",
            "identifier": "Mortar",
            "index": 3,
            "name": "Mortar"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Scale",
            "index": 4,
            "name": "Scale"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Mortar Size",
            "index": 5,
            "name": "Mortar Size"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Mortar Smooth",
            "index": 6,
            "name": "Mortar Smooth"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Bias",
            "index": 7,
            "name": "Bias"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Brick Width",
            "index": 8,
            "name": "Brick Width"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Row Height",
            "index": 9,
            "name": "Row Height"
        }
    ],
    "label": "Brick Texture",
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
def createShaderNodeTexBrick(self, name=None, color=None, label=None, x=None, y=None, color_mapping=None, offset=None, offset_frequency=None, squash=None, squash_frequency=None, texture_mapping=None, Vector=None, Color1=None, Color2=None, Mortar=None, Scale=None, Mortar_Size=None, Mortar_Smooth=None, Bias=None, Brick_Width=None, Row_Height=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeTexBrick"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["color_mapping"] = color_mapping
    node_def["attributes"]["offset"] = offset
    node_def["attributes"]["offset_frequency"] = offset_frequency
    node_def["attributes"]["squash"] = squash
    node_def["attributes"]["squash_frequency"] = squash_frequency
    node_def["attributes"]["texture_mapping"] = texture_mapping
    node_def["inputs"]["Vector"] = Vector
    node_def["inputs"]["Color1"] = Color1
    node_def["inputs"]["Color2"] = Color2
    node_def["inputs"]["Mortar"] = Mortar
    node_def["inputs"]["Scale"] = Scale
    node_def["inputs"]["Mortar Size"] = Mortar_Size
    node_def["inputs"]["Mortar Smooth"] = Mortar_Smooth
    node_def["inputs"]["Bias"] = Bias
    node_def["inputs"]["Brick Width"] = Brick_Width
    node_def["inputs"]["Row Height"] = Row_Height

    return self._create_node(node_def)
