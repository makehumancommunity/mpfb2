"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "bool",
            "name": "from_instancer",
            "sample_value": "False"
        },
        {
            "allowed_values": [],
            "class": "str",
            "name": "uv_map",
            "sample_value": ""
        }
    ],
    "class": "ShaderNodeUVMap",
    "inputs": [],
    "label": "UV Map",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "UV",
            "index": 0,
            "name": "UV"
        }
    ]
}"""
def createShaderNodeUVMap(self, name=None, color=None, label=None, x=None, y=None, from_instancer=None, uv_map=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeUVMap"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["from_instancer"] = from_instancer
    node_def["attributes"]["uv_map"] = uv_map

    return self._create_node(node_def)
