"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "mode",
            "sample_value": "RGB"
        }
    ],
    "class": "ShaderNodeSeparateColor",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        }
    ],
    "label": "Separate Color",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Red",
            "index": 0,
            "list_as_argument": false,
            "name": "Red"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Green",
            "index": 1,
            "list_as_argument": false,
            "name": "Green"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Blue",
            "index": 2,
            "list_as_argument": false,
            "name": "Blue"
        }
    ]
}"""
def createShaderNodeSeparateColor(self, name=None, color=None, label=None, x=None, y=None, mode=None, Color=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeSeparateColor"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["mode"] = mode
    node_def["inputs"]["Color"] = Color

    return self._create_node(node_def)
