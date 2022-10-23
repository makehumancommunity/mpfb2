"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "noise_dimensions",
            "sample_value": "3D"
        }
    ],
    "class": "ShaderNodeTexWhiteNoise",
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
        }
    ],
    "label": "White Noise Texture",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Value",
            "index": 0,
            "list_as_argument": false,
            "name": "Value"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 1,
            "list_as_argument": false,
            "name": "Color"
        }
    ]
}"""
def createShaderNodeTexWhiteNoise(self, name=None, color=None, label=None, x=None, y=None, noise_dimensions=None, Vector=None, W=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeTexWhiteNoise"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["noise_dimensions"] = noise_dimensions
    node_def["inputs"]["Vector"] = Vector
    node_def["inputs"]["W"] = W

    return self._create_node(node_def)
