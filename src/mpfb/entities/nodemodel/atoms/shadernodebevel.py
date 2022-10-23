"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "samples",
            "sample_value": "4"
        }
    ],
    "class": "ShaderNodeBevel",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Radius",
            "index": 0,
            "name": "Radius"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 1,
            "name": "Normal"
        }
    ],
    "label": "Bevel",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 0,
            "list_as_argument": false,
            "name": "Normal"
        }
    ]
}"""
def createShaderNodeBevel(self, name=None, color=None, label=None, x=None, y=None, samples=None, Radius=None, Normal=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeBevel"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["samples"] = samples
    node_def["inputs"]["Radius"] = Radius
    node_def["inputs"]["Normal"] = Normal

    return self._create_node(node_def)
