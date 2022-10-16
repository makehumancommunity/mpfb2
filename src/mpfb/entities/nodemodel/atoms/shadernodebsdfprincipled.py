"""
{
    "attributes": [
        {
            "allowed_values": [],
            "class": "enum",
            "name": "distribution",
            "sample_value": "GGX"
        },
        {
            "allowed_values": [],
            "class": "enum",
            "name": "subsurface_method",
            "sample_value": "RANDOM_WALK"
        }
    ],
    "class": "ShaderNodeBsdfPrincipled",
    "inputs": [
        {
            "class": "NodeSocketColor",
            "identifier": "Base Color",
            "index": 0,
            "name": "Base Color"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Subsurface",
            "index": 1,
            "name": "Subsurface"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Subsurface Radius",
            "index": 2,
            "name": "Subsurface Radius"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Subsurface Color",
            "index": 3,
            "name": "Subsurface Color"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Subsurface IOR",
            "index": 4,
            "name": "Subsurface IOR"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Subsurface Anisotropy",
            "index": 5,
            "name": "Subsurface Anisotropy"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Metallic",
            "index": 6,
            "name": "Metallic"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Specular",
            "index": 7,
            "name": "Specular"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Specular Tint",
            "index": 8,
            "name": "Specular Tint"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Roughness",
            "index": 9,
            "name": "Roughness"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Anisotropic",
            "index": 10,
            "name": "Anisotropic"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Anisotropic Rotation",
            "index": 11,
            "name": "Anisotropic Rotation"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Sheen",
            "index": 12,
            "name": "Sheen"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Sheen Tint",
            "index": 13,
            "name": "Sheen Tint"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Clearcoat",
            "index": 14,
            "name": "Clearcoat"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Clearcoat Roughness",
            "index": 15,
            "name": "Clearcoat Roughness"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "IOR",
            "index": 16,
            "name": "IOR"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Transmission",
            "index": 17,
            "name": "Transmission"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Transmission Roughness",
            "index": 18,
            "name": "Transmission Roughness"
        },
        {
            "class": "NodeSocketColor",
            "identifier": "Emission",
            "index": 19,
            "name": "Emission"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Emission Strength",
            "index": 20,
            "name": "Emission Strength"
        },
        {
            "class": "NodeSocketFloatFactor",
            "identifier": "Alpha",
            "index": 21,
            "name": "Alpha"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Normal",
            "index": 22,
            "name": "Normal"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Clearcoat Normal",
            "index": 23,
            "name": "Clearcoat Normal"
        },
        {
            "class": "NodeSocketVector",
            "identifier": "Tangent",
            "index": 24,
            "name": "Tangent"
        },
        {
            "class": "NodeSocketFloat",
            "identifier": "Weight",
            "index": 25,
            "name": "Weight"
        }
    ],
    "label": "Principled BSDF",
    "outputs": [
        {
            "class": "NodeSocketShader",
            "identifier": "BSDF",
            "index": 0,
            "name": "BSDF"
        }
    ]
}"""
def createShaderNodeBsdfPrincipled(self, name=None, color=None, label=None, x=None, y=None, distribution=None, subsurface_method=None, Base_Color=None, Subsurface=None, Subsurface_Radius=None, Subsurface_Color=None, Subsurface_IOR=None, Subsurface_Anisotropy=None, Metallic=None, Specular=None, Specular_Tint=None, Roughness=None, Anisotropic=None, Anisotropic_Rotation=None, Sheen=None, Sheen_Tint=None, Clearcoat=None, Clearcoat_Roughness=None, IOR=None, Transmission=None, Transmission_Roughness=None, Emission=None, Emission_Strength=None, Alpha=None, Normal=None, Clearcoat_Normal=None, Tangent=None, Weight=None):
    node_def = dict()
    node_def["attributes"] = dict()
    node_def["inputs"] = dict()
    node_def["class"] = "ShaderNodeBsdfPrincipled"
    node_def["name"] = name
    node_def["color"] = color
    node_def["label"] = label
    node_def["x"] = x
    node_def["y"] = y
    node_def["attributes"]["distribution"] = distribution
    node_def["attributes"]["subsurface_method"] = subsurface_method
    node_def["inputs"]["Base Color"] = Base_Color
    node_def["inputs"]["Subsurface"] = Subsurface
    node_def["inputs"]["Subsurface Radius"] = Subsurface_Radius
    node_def["inputs"]["Subsurface Color"] = Subsurface_Color
    node_def["inputs"]["Subsurface IOR"] = Subsurface_IOR
    node_def["inputs"]["Subsurface Anisotropy"] = Subsurface_Anisotropy
    node_def["inputs"]["Metallic"] = Metallic
    node_def["inputs"]["Specular"] = Specular
    node_def["inputs"]["Specular Tint"] = Specular_Tint
    node_def["inputs"]["Roughness"] = Roughness
    node_def["inputs"]["Anisotropic"] = Anisotropic
    node_def["inputs"]["Anisotropic Rotation"] = Anisotropic_Rotation
    node_def["inputs"]["Sheen"] = Sheen
    node_def["inputs"]["Sheen Tint"] = Sheen_Tint
    node_def["inputs"]["Clearcoat"] = Clearcoat
    node_def["inputs"]["Clearcoat Roughness"] = Clearcoat_Roughness
    node_def["inputs"]["IOR"] = IOR
    node_def["inputs"]["Transmission"] = Transmission
    node_def["inputs"]["Transmission Roughness"] = Transmission_Roughness
    node_def["inputs"]["Emission"] = Emission
    node_def["inputs"]["Emission Strength"] = Emission_Strength
    node_def["inputs"]["Alpha"] = Alpha
    node_def["inputs"]["Normal"] = Normal
    node_def["inputs"]["Clearcoat Normal"] = Clearcoat_Normal
    node_def["inputs"]["Tangent"] = Tangent
    node_def["inputs"]["Weight"] = Weight

    return self._create_node(node_def)
