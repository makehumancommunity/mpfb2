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
        "component": {
            "class": "str",
            "name": "component",
            "value": "Reflection"
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
    "class": "ShaderNodeBsdfHair",
    "inputs": {
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
        "Offset": {
            "class": "NodeSocketFloatAngle",
            "default_value": 0.0,
            "identifier": "Offset",
            "name": "Offset",
            "value_type": "VALUE"
        },
        "RoughnessU": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.10000000149011612,
            "identifier": "RoughnessU",
            "name": "RoughnessU",
            "value_type": "VALUE"
        },
        "RoughnessV": {
            "class": "NodeSocketFloatFactor",
            "default_value": 1.0,
            "identifier": "RoughnessV",
            "name": "RoughnessV",
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

class _NodeWrapperShaderNodeBsdfHair(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snBsdfHair = _NodeWrapperShaderNodeBsdfHair()
