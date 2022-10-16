"""
{
    "attributes": [],
    "class": "ShaderNodeFresnel",
    "inputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "IOR",
            "index": 0,
            "name": "IOR"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 1,
            "name": "Normal"
        }
    ],
    "label": "Fresnel",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Fac",
            "index": 0,
            "name": "Fac"
        }
    ]
}"""
def createShaderNodeFresnel(self, name=None, color=None, label=None, x=None, y=None, IOR=None, Normal=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeFresnel"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["inputs"]["IOR"] = IOR
    node_def["inputs"]["Normal"] = Normal

    return self._create_node(node_def)
