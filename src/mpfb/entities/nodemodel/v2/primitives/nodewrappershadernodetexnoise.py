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
        "noise_dimensions": {
            "class": "enum",
            "name": "noise_dimensions",
            "value": "3D"
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeTexNoise",
    "inputs": {
        "Detail": {
            "class": "NodeSocketFloat",
            "default_value": 2.0,
            "identifier": "Detail",
            "name": "Detail",
            "value_type": "VALUE"
        },
        "Distortion": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Distortion",
            "name": "Distortion",
            "value_type": "VALUE"
        },
        "Roughness": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.5,
            "identifier": "Roughness",
            "name": "Roughness",
            "value_type": "VALUE"
        },
        "Scale": {
            "class": "NodeSocketFloat",
            "default_value": 5.0,
            "identifier": "Scale",
            "name": "Scale",
            "value_type": "VALUE"
        },
        "Vector": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Vector",
            "name": "Vector",
            "value_type": "VECTOR"
        },
        "W": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "W",
            "name": "W",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Color",
            "name": "Color",
            "value_type": "RGBA"
        },
        "Fac": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Fac",
            "name": "Fac",
            "value_type": "VALUE"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeTexNoise(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snTexNoise = _NodeWrapperShaderNodeTexNoise()
