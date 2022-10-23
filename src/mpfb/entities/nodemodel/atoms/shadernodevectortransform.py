"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "convert_from",
            "sample_value": "WORLD"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "convert_to",
            "sample_value": "OBJECT"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "vector_type",
            "sample_value": "VECTOR"
        }
    ],
    "class": "ShaderNodeVectorTransform",
    "inputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "name": "Vector"
        }
    ],
    "label": "Vector Transform",
    "outputs": [
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 0,
            "list_as_argument": false,
            "name": "Vector"
        }
    ]
}"""
def createShaderNodeVectorTransform(self, name=None, color=None, label=None, x=None, y=None, convert_from=None, convert_to=None, vector_type=None, Vector=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeVectorTransform"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["convert_from"] = convert_from
    node_def["attributes"]["convert_to"] = convert_to
    node_def["attributes"]["vector_type"] = vector_type
    node_def["inputs"]["Vector"] = Vector

    return self._create_node(node_def)
