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
    "class": "ShaderNodeCombineColor",
    "inputs": [
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Red",
            "index": 0,
            "name": "Red"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Green",
            "index": 1,
            "name": "Green"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Blue",
            "index": 2,
            "name": "Blue"
        }
    ],
    "label": "Combine Color",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        }
    ]
}"""
def createShaderNodeCombineColor(self, name=None, color=None, label=None, x=None, y=None, mode=None, Red=None, Green=None, Blue=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeCombineColor"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["mode"] = mode
    node_def["inputs"]["Red"] = Red
    node_def["inputs"]["Green"] = Green
    node_def["inputs"]["Blue"] = Blue

    return self._create_node(node_def)
