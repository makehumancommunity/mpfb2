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
            "list_as_argument": false,
            "name": "Position"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 1,
            "list_as_argument": false,
            "name": "Normal"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Tangent",
            "index": 2,
            "list_as_argument": false,
            "name": "Tangent"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "True Normal",
            "index": 3,
            "list_as_argument": false,
            "name": "True Normal"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Incoming",
            "index": 4,
            "list_as_argument": false,
            "name": "Incoming"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Parametric",
            "index": 5,
            "list_as_argument": false,
            "name": "Parametric"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Backfacing",
            "index": 6,
            "list_as_argument": false,
            "name": "Backfacing"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Pointiness",
            "index": 7,
            "list_as_argument": false,
            "name": "Pointiness"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Random Per Island",
            "index": 8,
            "list_as_argument": false,
            "name": "Random Per Island"
        }
    ]
}"""
def createShaderNodeNewGeometry(self, name=None, color=None, label=None, x=None, y=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeNewGeometry"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y

    return self._create_node(node_def)
