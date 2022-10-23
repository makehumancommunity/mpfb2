"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "bool",
            "name": "use_pixel_size",
            "sample_value": "False"
        }
    ],
    "class": "ShaderNodeWireframe",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Size",
            "index": 0,
            "name": "Size"
        }
    ],
    "label": "Wireframe",
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
def createShaderNodeWireframe(self, name=None, color=None, label=None, x=None, y=None, use_pixel_size=None, Size=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeWireframe"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["use_pixel_size"] = use_pixel_size
    node_def["inputs"]["Size"] = Size

    return self._create_node(node_def)
