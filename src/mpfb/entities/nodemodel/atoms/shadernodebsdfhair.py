"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "str",
            "name": "component",
            "sample_value": "Reflection"
        }
    ],
    "class": "ShaderNodeBsdfHair",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloatAngle",
            "identifier": "Offset",
            "index": 1,
            "name": "Offset"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "RoughnessU",
            "index": 2,
            "name": "RoughnessU"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "RoughnessV",
            "index": 3,
            "name": "RoughnessV"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Tangent",
            "index": 4,
            "name": "Tangent"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Weight",
            "index": 5,
            "name": "Weight"
        }
    ],
    "label": "Hair BSDF",
    "outputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "BSDF",
            "index": 0,
            "name": "BSDF"
        }
    ]
}"""
def createShaderNodeBsdfHair(self, name=None, color=None, label=None, x=None, y=None, component=None, Color=None, Offset=None, RoughnessU=None, RoughnessV=None, Tangent=None, Weight=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeBsdfHair"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["component"] = component
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Offset"] = Offset
    node_def["inputs"]["RoughnessU"] = RoughnessU
    node_def["inputs"]["RoughnessV"] = RoughnessV
    node_def["inputs"]["Tangent"] = Tangent
    node_def["inputs"]["Weight"] = Weight

    return self._create_node(node_def)
