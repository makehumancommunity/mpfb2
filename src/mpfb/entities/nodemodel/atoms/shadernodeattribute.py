"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "str",
            "name": "attribute_name",
            "sample_value": ""
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "attribute_type",
            "sample_value": "GEOMETRY"
        }
    ],
    "class": "ShaderNodeAttribute",
    "inputs": [],
    "label": "Attribute",
    "outputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Vector",
            "index": 1,
            "name": "Vector"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Fac",
            "index": 2,
            "name": "Fac"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Alpha",
            "index": 3,
            "name": "Alpha"
        }
    ]
}"""
def createShaderNodeAttribute(self, name=None, color=None, label=None, x=None, y=None, attribute_name=None, attribute_type=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeAttribute"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["attribute_name"] = attribute_name
    node_def["attributes"]["attribute_type"] = attribute_type

    return self._create_node(node_def)
