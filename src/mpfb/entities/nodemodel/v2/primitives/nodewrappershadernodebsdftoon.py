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
            "class": "enum",
            "name": "component",
            "value": "DIFFUSE"
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
    "class": "ShaderNodeBsdfToon",
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
        "Size": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.5,
            "identifier": "Size",
            "name": "Size",
            "value_type": "VALUE"
        },
        "Smooth": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Smooth",
            "name": "Smooth",
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

class _NodeWrapperShaderNodeBsdfToon(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snBsdfToon = _NodeWrapperShaderNodeBsdfToon()
