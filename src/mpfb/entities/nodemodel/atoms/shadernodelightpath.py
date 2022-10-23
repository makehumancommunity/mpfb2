"""
{
    "attributes": [],
    "class": "ShaderNodeLightPath",
    "inputs": [],
    "label": "Light Path",
    "outputs": [
        {
            "class": "NodeSocketFloat",
            "identifier": "Is Camera Ray",
            "index": 0,
            "list_as_argument": false,
            "name": "Is Camera Ray"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Is Shadow Ray",
            "index": 1,
            "list_as_argument": false,
            "name": "Is Shadow Ray"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Is Diffuse Ray",
            "index": 2,
            "list_as_argument": false,
            "name": "Is Diffuse Ray"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Is Glossy Ray",
            "index": 3,
            "list_as_argument": false,
            "name": "Is Glossy Ray"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Is Singular Ray",
            "index": 4,
            "list_as_argument": false,
            "name": "Is Singular Ray"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Is Reflection Ray",
            "index": 5,
            "list_as_argument": false,
            "name": "Is Reflection Ray"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Is Transmission Ray",
            "index": 6,
            "list_as_argument": false,
            "name": "Is Transmission Ray"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Ray Length",
            "index": 7,
            "list_as_argument": false,
            "name": "Ray Length"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Ray Depth",
            "index": 8,
            "list_as_argument": false,
            "name": "Ray Depth"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Diffuse Depth",
            "index": 9,
            "list_as_argument": false,
            "name": "Diffuse Depth"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Glossy Depth",
            "index": 10,
            "list_as_argument": false,
            "name": "Glossy Depth"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Transparent Depth",
            "index": 11,
            "list_as_argument": false,
            "name": "Transparent Depth"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Transmission Depth",
            "index": 12,
            "list_as_argument": false,
            "name": "Transmission Depth"
        }
    ]
}"""
def createShaderNodeLightPath(self, name=None, color=None, label=None, x=None, y=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeLightPath"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y

    return self._create_node(node_def)
