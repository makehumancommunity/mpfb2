"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "color_mapping",
            "sample_value": "<bpy_struct, ColorMapping at 0x7ff288097c98>"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "musgrave_dimensions",
            "sample_value": "3D"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "musgrave_type",
            "sample_value": "FBM"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "texture_mapping",
            "sample_value": "<bpy_struct, TexMapping at 0x7ff288097c08>"
        }
    ],
    "class": "ShaderNodeTexMusgrave",
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
            "class": "NodeSocketFloat",
            "identifier": "Dimension",
            "index": 4,
            "name": "Dimension"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Lacunarity",
            "index": 5,
            "name": "Lacunarity"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Offset",
            "index": 6,
            "name": "Offset"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Gain",
            "index": 7,
            "name": "Gain"
        }
    ],
    "label": "Musgrave Texture",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Fac",
            "index": 0,
            "list_as_argument": false,
            "name": "Fac"
        }
    ]
}"""
def createShaderNodeTexMusgrave(self, name=None, color=None, label=None, x=None, y=None, color_mapping=None, musgrave_dimensions=None, musgrave_type=None, texture_mapping=None, Vector=None, W=None, Scale=None, Detail=None, Dimension=None, Lacunarity=None, Offset=None, Gain=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeTexMusgrave"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["color_mapping"] = color_mapping
    node_def["attributes"]["musgrave_dimensions"] = musgrave_dimensions
    node_def["attributes"]["musgrave_type"] = musgrave_type
    node_def["attributes"]["texture_mapping"] = texture_mapping
    node_def["inputs"]["Vector"] = Vector
    node_def["inputs"]["W"] = W
    node_def["inputs"]["Scale"] = Scale
    node_def["inputs"]["Detail"] = Detail
    node_def["inputs"]["Dimension"] = Dimension
    node_def["inputs"]["Lacunarity"] = Lacunarity
    node_def["inputs"]["Offset"] = Offset
    node_def["inputs"]["Gain"] = Gain

    return self._create_node(node_def)
