"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "color_mapping",
            "sample_value": "<bpy_struct, ColorMapping at 0x7ff288097898>"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "distance",
            "sample_value": "EUCLIDEAN"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "feature",
            "sample_value": "F1"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "texture_mapping",
            "sample_value": "<bpy_struct, TexMapping at 0x7ff288097808>"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "voronoi_dimensions",
            "sample_value": "3D"
        }
    ],
    "class": "ShaderNodeTexVoronoi",
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
            "class": "NodeSocketFloatFactor",
            "identifier": "Smoothness",
            "index": 3,
            "name": "Smoothness"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Exponent",
            "index": 4,
            "name": "Exponent"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Randomness",
            "index": 5,
            "name": "Randomness"
        }
    ],
    "label": "Voronoi Texture",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Distance",
            "index": 0,
            "list_as_argument": false,
            "name": "Distance"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 1,
            "list_as_argument": false,
            "name": "Color"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Position",
            "index": 2,
            "list_as_argument": false,
            "name": "Position"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "W",
            "index": 3,
            "list_as_argument": false,
            "name": "W"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Radius",
            "index": 4,
            "list_as_argument": false,
            "name": "Radius"
        }
    ]
}"""
def createShaderNodeTexVoronoi(self, name=None, color=None, label=None, x=None, y=None, color_mapping=None, distance=None, feature=None, texture_mapping=None, voronoi_dimensions=None, Vector=None, W=None, Scale=None, Smoothness=None, Exponent=None, Randomness=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeTexVoronoi"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["color_mapping"] = color_mapping
    node_def["attributes"]["distance"] = distance
    node_def["attributes"]["feature"] = feature
    node_def["attributes"]["texture_mapping"] = texture_mapping
    node_def["attributes"]["voronoi_dimensions"] = voronoi_dimensions
    node_def["inputs"]["Vector"] = Vector
    node_def["inputs"]["W"] = W
    node_def["inputs"]["Scale"] = Scale
    node_def["inputs"]["Smoothness"] = Smoothness
    node_def["inputs"]["Exponent"] = Exponent
    node_def["inputs"]["Randomness"] = Randomness

    return self._create_node(node_def)
