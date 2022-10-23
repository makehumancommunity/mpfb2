"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "parametrization",
            "sample_value": "COLOR"
        }
    ],
    "class": "ShaderNodeBsdfHairPrincipled",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Color",
            "index": 0,
            "name": "Color"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Melanin",
            "index": 1,
            "name": "Melanin"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Melanin Redness",
            "index": 2,
            "name": "Melanin Redness"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Tint",
            "index": 3,
            "name": "Tint"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Absorption Coefficient",
            "index": 4,
            "name": "Absorption Coefficient"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Roughness",
            "index": 5,
            "name": "Roughness"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Radial Roughness",
            "index": 6,
            "name": "Radial Roughness"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Coat",
            "index": 7,
            "name": "Coat"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "IOR",
            "index": 8,
            "name": "IOR"
        },
        {
            "class": "NodeSocketFloatAngle",
            "identifier": "Offset",
            "index": 9,
            "name": "Offset"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Random Color",
            "index": 10,
            "name": "Random Color"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Random Roughness",
            "index": 11,
            "name": "Random Roughness"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Random",
            "index": 12,
            "name": "Random"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Weight",
            "index": 13,
            "name": "Weight"
        }
    ],
    "label": "Principled Hair BSDF",
    "outputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "BSDF",
            "index": 0,
            "list_as_argument": false,
            "name": "BSDF"
        }
    ]
}"""
def createShaderNodeBsdfHairPrincipled(self, name=None, color=None, label=None, x=None, y=None, parametrization=None, Color=None, Melanin=None, Melanin_Redness=None, Tint=None, Absorption_Coefficient=None, Roughness=None, Radial_Roughness=None, Coat=None, IOR=None, Offset=None, Random_Color=None, Random_Roughness=None, Random=None, Weight=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["outputs"] = dict()
    node_def["class"] = "ShaderNodeBsdfHairPrincipled"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["parametrization"] = parametrization
    node_def["inputs"]["Color"] = Color
    node_def["inputs"]["Melanin"] = Melanin
    node_def["inputs"]["Melanin Redness"] = Melanin_Redness
    node_def["inputs"]["Tint"] = Tint
    node_def["inputs"]["Absorption Coefficient"] = Absorption_Coefficient
    node_def["inputs"]["Roughness"] = Roughness
    node_def["inputs"]["Radial Roughness"] = Radial_Roughness
    node_def["inputs"]["Coat"] = Coat
    node_def["inputs"]["IOR"] = IOR
    node_def["inputs"]["Offset"] = Offset
    node_def["inputs"]["Random Color"] = Random_Color
    node_def["inputs"]["Random Roughness"] = Random_Roughness
    node_def["inputs"]["Random"] = Random
    node_def["inputs"]["Weight"] = Weight

    return self._create_node(node_def)
