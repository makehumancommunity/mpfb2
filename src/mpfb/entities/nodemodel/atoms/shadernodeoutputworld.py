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
    "class": "ShaderNodeOutputWorld",
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
        }
    ],
    "label": "World Output",
    "outputs": []
}"""
def createShaderNodeOutputWorld(self, name=None, color=None, label=None, x=None, y=None, is_active_output=None, target=None, Surface=None, Volume=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeOutputWorld"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["is_active_output"] = is_active_output
    node_def["attributes"]["target"] = target
    node_def["inputs"]["Surface"] = Surface
    node_def["inputs"]["Volume"] = Volume

    return self._create_node(node_def)
