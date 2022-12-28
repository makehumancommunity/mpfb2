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
        "falloff": {
            "class": "enum",
            "name": "falloff",
            "value": "RANDOM_WALK"
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
    "class": "ShaderNodeSubsurfaceScattering",
    "inputs": {
        "Anisotropy": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
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
        "IOR": {
            "class": "NodeSocketFloatFactor",
            "default_value": 1.399999976158142,
            "identifier": "IOR",
            "name": "IOR",
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
        "Radius": {
            "class": "NodeSocketVector",
            "default_value": [
                1.0,
                0.20000000298023224,
                0.10000000149011612
            ],
            "identifier": "Radius",
            "name": "Radius",
            "value_type": "VECTOR"
        },
        "Scale": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Scale",
            "name": "Scale",
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
        "BSSRDF": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "BSSRDF",
            "name": "BSSRDF",
            "value_type": "SHADER"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeSubsurfaceScattering(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snSubsurfaceScattering = _NodeWrapperShaderNodeSubsurfaceScattering()
