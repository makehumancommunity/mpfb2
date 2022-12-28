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
        "width": {
            "class": "float",
            "name": "width",
            "value": 150.0
        }
    },
    "class": "ShaderNodeBsdfAnisotropic",
    "inputs": {
        "Anisotropy": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Anisotropy",
            "name": "Anisotropy",
            "value_type": "VALUE"
        },
        "Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.800000011920929,
                0.800000011920929,
                0.800000011920929,
                1.0
            ],
            "identifier": "Color",
            "name": "Color",
            "value_type": "RGBA"
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
        "Rotation": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Rotation",
            "name": "Rotation",
            "value_type": "VALUE"
        },
        "Roughness": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.5,
            "identifier": "Roughness",
            "name": "Roughness",
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

class _NodeWrapperShaderNodeBsdfAnisotropic(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snBsdfAnisotropic = _NodeWrapperShaderNodeBsdfAnisotropic()
