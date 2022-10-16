"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "str",
            "name": "bytecode",
            "sample_value": ""
        },
        {
            "allowed_values": [],
            "class": "str",
            "name": "bytecode_hash",
            "sample_value": ""
        },
        {
            "allowed_values": [],
            "class": "str",
            "name": "filepath",
            "sample_value": ""
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "mode",
            "sample_value": "INTERNAL"
        },
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "script",
            "sample_value": "None"
        },
        {
            "allowed_values": [],
            "class": "bool",
            "name": "use_auto_update",
            "sample_value": "False"
        }
    ],
    "class": "ShaderNodeScript",
    "inputs": [],
    "label": "Script",
    "outputs": []
}"""
def createShaderNodeScript(self, name=None, color=None, label=None, x=None, y=None, bytecode=None, bytecode_hash=None, filepath=None, mode=None, script=None, use_auto_update=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeScript"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["bytecode"] = bytecode
    node_def["attributes"]["bytecode_hash"] = bytecode_hash
    node_def["attributes"]["filepath"] = filepath
    node_def["attributes"]["mode"] = mode
    node_def["attributes"]["script"] = script
    node_def["attributes"]["use_auto_update"] = use_auto_update

    return self._create_node(node_def)
