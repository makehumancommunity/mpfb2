"""
{
    "attributes": [],
    "class": "ShaderNodeNewGeometry",
    "inputs": [],
    "label": "Geometry",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Position",
            "index": 0,
            "name": "Position"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 1,
            "name": "Normal"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Tangent",
            "index": 2,
            "name": "Tangent"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "True Normal",
            "index": 3,
            "name": "True Normal"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Incoming",
            "index": 4,
            "name": "Incoming"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Parametric",
            "index": 5,
            "name": "Parametric"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Backfacing",
            "index": 6,
            "name": "Backfacing"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Pointiness",
            "index": 7,
            "name": "Pointiness"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Random Per Island",
            "index": 8,
            "name": "Random Per Island"
        }
    ]
}"""
def createShaderNodeNewGeometry(self, name=None, color=None, label=None, x=None, y=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeNewGeometry"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y

    return self._create_node(node_def)
