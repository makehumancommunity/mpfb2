"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "bool",
            "name": "is_active_output",
            "sample_value": "False"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "target",
            "sample_value": "ALL"
        }
    ],
    "class": "ShaderNodeOutputMaterial",
    "inputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "Surface",
            "index": 0,
            "name": "Surface"
        },
        {
            "class": "NodeSocketShader",
            "identifier": "Volume",
            "index": 1,
            "name": "Volume"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Displacement",
            "index": 2,
            "name": "Displacement"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Thickness",
            "index": 3,
            "name": "Thickness"
        }
    ],
    "label": "Material Output",
    "outputs": []
}"""
def createShaderNodeOutputMaterial(self, name=None, color=None, label=None, x=None, y=None, is_active_output=None, target=None, Surface=None, Volume=None, Displacement=None, Thickness=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeOutputMaterial"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["is_active_output"] = is_active_output
    node_def["attributes"]["target"] = target
    node_def["inputs"]["Surface"] = Surface
    node_def["inputs"]["Volume"] = Volume
    node_def["inputs"]["Displacement"] = Displacement
    node_def["inputs"]["Thickness"] = Thickness

    return self._create_node(node_def)
