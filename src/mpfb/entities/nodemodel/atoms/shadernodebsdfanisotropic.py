"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "distribution",
            "sample_value": "GGX"
        }
    ],
    "class": "ShaderNodeBsdfAnisotropic",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Roughness",
            "index": 1,
            "name": "Roughness"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Anisotropy",
            "index": 2,
            "name": "Anisotropy"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Rotation",
            "index": 3,
            "name": "Rotation"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 4,
            "name": "Normal"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Tangent",
            "index": 5,
            "name": "Tangent"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Weight",
            "index": 6,
            "name": "Weight"
        }
    ],
    "label": "Anisotropic BSDF",
    "outputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "BSDF",
            "index": 0,
            "name": "BSDF"
        }
    ]
}"""
def createShaderNodeBsdfAnisotropic(self, name=None, color=None, label=None, x=None, y=None, distribution=None, Color=None, Roughness=None, Anisotropy=None, Rotation=None, Normal=None, Tangent=None, Weight=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeBsdfAnisotropic"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["distribution"] = distribution
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Roughness"] = Roughness
    node_def["inputs"]["Anisotropy"] = Anisotropy
    node_def["inputs"]["Rotation"] = Rotation
    node_def["inputs"]["Normal"] = Normal
    node_def["inputs"]["Tangent"] = Tangent
    node_def["inputs"]["Weight"] = Weight

    return self._create_node(node_def)
