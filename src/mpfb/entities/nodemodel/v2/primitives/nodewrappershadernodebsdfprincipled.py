import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "attributes": {
        "color": {
            "class": "Color",
            "name": "color",
            "value": [
                0.608,
                0.608,
                0.608
            ]
        },
        "distribution": {
            "class": "enum",
            "name": "distribution",
            "value": "MULTI_GGX"
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
            "value": "RANDOM_WALK_SKIN"
        },
        "use_custom_color": {
            "class": "bool",
            "name": "use_custom_color",
            "value": false
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
                0.8,
                0.8,
                0.8,
                1.0
            ],
            "identifier": "Base Color",
            "name": "Base Color",
            "value_type": "RGBA"
        },
        "Coat IOR": {
            "class": "NodeSocketFloat",
            "default_value": 1.5,
            "identifier": "Coat IOR",
            "name": "Coat IOR",
            "value_type": "VALUE"
        },
        "Coat Normal": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Coat Normal",
            "name": "Coat Normal",
            "value_type": "VECTOR"
        },
        "Coat Roughness": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.03,
            "identifier": "Coat Roughness",
            "name": "Coat Roughness",
            "value_type": "VALUE"
        },
        "Coat Tint": {
            "class": "NodeSocketColor",
            "default_value": [
                1.0,
                1.0,
                1.0,
                1.0
            ],
            "identifier": "Coat Tint",
            "name": "Coat Tint",
            "value_type": "RGBA"
        },
        "Coat Weight": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Coat Weight",
            "name": "Coat Weight",
            "value_type": "VALUE"
        },
        "Emission Color": {
            "class": "NodeSocketColor",
            "default_value": [
                1.0,
                1.0,
                1.0,
                1.0
            ],
            "identifier": "Emission Color",
            "name": "Emission Color",
            "value_type": "RGBA"
        },
        "Emission Strength": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Emission Strength",
            "name": "Emission Strength",
            "value_type": "VALUE"
        },
        "IOR": {
            "class": "NodeSocketFloat",
            "default_value": 1.45,
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
        "Sheen Roughness": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.5,
            "identifier": "Sheen Roughness",
            "name": "Sheen Roughness",
            "value_type": "VALUE"
        },
        "Sheen Tint": {
            "class": "NodeSocketColor",
            "default_value": [
                1.0,
                1.0,
                1.0,
                1.0
            ],
            "identifier": "Sheen Tint",
            "name": "Sheen Tint",
            "value_type": "RGBA"
        },
        "Sheen Weight": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Sheen Weight",
            "name": "Sheen Weight",
            "value_type": "VALUE"
        },
        "Specular IOR Level": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.5,
            "identifier": "Specular IOR Level",
            "name": "Specular IOR Level",
            "value_type": "VALUE"
        },
        "Specular Tint": {
            "class": "NodeSocketColor",
            "default_value": [
                1.0,
                1.0,
                1.0,
                1.0
            ],
            "identifier": "Specular Tint",
            "name": "Specular Tint",
            "value_type": "RGBA"
        },
        "Subsurface Anisotropy": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Subsurface Anisotropy",
            "name": "Subsurface Anisotropy",
            "value_type": "VALUE"
        },
        "Subsurface IOR": {
            "class": "NodeSocketFloatFactor",
            "default_value": 1.4,
            "identifier": "Subsurface IOR",
            "name": "Subsurface IOR",
            "value_type": "VALUE"
        },
        "Subsurface Radius": {
            "class": "NodeSocketVector",
            "default_value": [
                1.0,
                0.2,
                0.1
            ],
            "identifier": "Subsurface Radius",
            "name": "Subsurface Radius",
            "value_type": "VECTOR"
        },
        "Subsurface Scale": {
            "class": "NodeSocketFloatDistance",
            "default_value": 0.05,
            "identifier": "Subsurface Scale",
            "name": "Subsurface Scale",
            "value_type": "VALUE"
        },
        "Subsurface Weight": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Subsurface Weight",
            "name": "Subsurface Weight",
            "value_type": "VALUE"
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
        "Transmission Weight": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Transmission Weight",
            "name": "Transmission Weight",
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
