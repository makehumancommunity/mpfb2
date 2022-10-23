"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "interface",
            "sample_value": "<bpy_struct, PropertyGroup(\"\") at 0x7ff288124008>"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "node_tree",
            "sample_value": "None"
        }
    ],
    "class": "ShaderNodeGroup",
    "inputs": [],
    "label": "Group",
    "outputs": []
}"""
def createShaderNodeGroup(self, name=None, color=None, label=None, x=None, y=None, interface=None, node_tree=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeGroup"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["interface"] = interface
    node_def["attributes"]["node_tree"] = node_tree

    return self._create_node(node_def)
