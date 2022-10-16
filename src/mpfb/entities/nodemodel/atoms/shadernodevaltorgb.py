"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "unknown",
            "name": "color_ramp",
            "sample_value": "<bpy_struct, ColorRamp at 0x7f6419411188>"
        }
    ],
    "class": "ShaderNodeValToRGB",
    "inputs": [
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Fac",
            "index": 0,
            "name": "Fac"
        }
    ],
    "label": "ColorRamp",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Alpha",
            "index": 1,
            "name": "Alpha"
        }
    ]
}"""
def createShaderNodeValToRGB(self, name=None, color=None, label=None, x=None, y=None, color_ramp=None, Fac=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeValToRGB"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["color_ramp"] = color_ramp
    node_def["inputs"]["Fac"] = Fac

    return self._create_node(node_def)
