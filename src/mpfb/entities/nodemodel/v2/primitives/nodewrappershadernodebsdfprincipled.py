import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "attributes": {
        "color": {
            "class": "Color",
            "name": "color",
            "value": [
                0.6079999804496765,
                0.6079999804496765,
                0.6079999804496765
            ]
        },
        "distribution": {
            "class": "enum",
            "name": "distribution",
            "value": "GGX"
        },
        "height": {
            "class": "float",
            "name": "height",
            "value": 100.0
        },
        "location": {
            "class": "Vector",
            "name": "location",
            "value": [
                0.0,
                0.0
            ]
        },
        "subsurface_method": {
            "class": "enum",
            "name": "subsurface_method",
            "value": "RANDOM_WALK"
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 240.0
        }
    },
    "class": "ShaderNodeBsdfPrincipled",
    "inputs": {
        "Alpha": {
            "class": "NodeSocketFloatFactor",
            "default_value": 1.0,
            "identifier": "Alpha",
            "name": "Alpha",
            "value_type": "VALUE"
        },
        "Anisotropic": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Anisotropic",
            "name": "Anisotropic",
            "value_type": "VALUE"
        },
        "Anisotropic Rotation": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Anisotropic Rotation",
            "name": "Anisotropic Rotation",
            "value_type": "VALUE"
        },
        "Base Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.800000011920929,
                0.800000011920929,
                0.800000011920929,
                1.0
            ],
            "identifier": "Base Color",
            "name": "Base Color",
            "value_type": "RGBA"
        },
        "Clearcoat": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Clearcoat",
            "name": "Clearcoat",
            "value_type": "VALUE"
        },
        "Clearcoat Normal": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Clearcoat Normal",
            "name": "Clearcoat Normal",
            "value_type": "VECTOR"
        },
        "Clearcoat Roughness": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.029999999329447746,
            "identifier": "Clearcoat Roughness",
            "name": "Clearcoat Roughness",
            "value_type": "VALUE"
        },
        "Emission": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                1.0
            ],
            "identifier": "Emission",
            "name": "Emission",
            "value_type": "RGBA"
        },
        "Emission Strength": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Emission Strength",
            "name": "Emission Strength",
            "value_type": "VALUE"
        },
        "IOR": {
            "class": "NodeSocketFloat",
            "default_value": 1.4500000476837158,
            "identifier": "IOR",
            "name": "IOR",
            "value_type": "VALUE"
        },
        "Metallic": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Metallic",
            "name": "Metallic",
            "value_type": "VALUE"
        },
        "Normal": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Normal",
            "name": "Normal",
            "value_type": "VECTOR"
        },
        "Roughness": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.5,
            "identifier": "Roughness",
            "name": "Roughness",
            "value_type": "VALUE"
        },
        "Sheen": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Sheen",
            "name": "Sheen",
            "value_type": "VALUE"
        },
        "Sheen Tint": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.5,
            "identifier": "Sheen Tint",
            "name": "Sheen Tint",
            "value_type": "VALUE"
        },
        "Specular": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.5,
            "identifier": "Specular",
            "name": "Specular",
            "value_type": "VALUE"
        },
        "Specular Tint": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Specular Tint",
            "name": "Specular Tint",
            "value_type": "VALUE"
        },
        "Subsurface": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Subsurface",
            "name": "Subsurface",
            "value_type": "VALUE"
        },
        "Subsurface Anisotropy": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Subsurface Anisotropy",
            "name": "Subsurface Anisotropy",
            "value_type": "VALUE"
        },
        "Subsurface Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.800000011920929,
                0.800000011920929,
                0.800000011920929,
                1.0
            ],
            "identifier": "Subsurface Color",
            "name": "Subsurface Color",
            "value_type": "RGBA"
        },
        "Subsurface IOR": {
            "class": "NodeSocketFloatFactor",
            "default_value": 1.399999976158142,
            "identifier": "Subsurface IOR",
            "name": "Subsurface IOR",
            "value_type": "VALUE"
        },
        "Subsurface Radius": {
            "class": "NodeSocketVector",
            "default_value": [
                1.0,
                0.20000000298023224,
                0.10000000149011612
            ],
            "identifier": "Subsurface Radius",
            "name": "Subsurface Radius",
            "value_type": "VECTOR"
        },
        "Tangent": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Tangent",
            "name": "Tangent",
            "value_type": "VECTOR"
        },
        "Transmission": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Transmission",
            "name": "Transmission",
            "value_type": "VALUE"
        },
        "Transmission Roughness": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Transmission Roughness",
            "name": "Transmission Roughness",
            "value_type": "VALUE"
        },
        "Weight": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Weight",
            "name": "Weight",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "BSDF": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "BSDF",
            "name": "BSDF",
            "value_type": "SHADER"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeBsdfPrincipled(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snBsdfPrincipled = _NodeWrapperShaderNodeBsdfPrincipled()
