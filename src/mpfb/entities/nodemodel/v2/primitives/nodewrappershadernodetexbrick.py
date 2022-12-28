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
        "offset": {
            "class": "float",
            "name": "offset",
            "value": 0.5
        },
        "offset_frequency": {
            "class": "int",
            "name": "offset_frequency",
            "value": 2
        },
        "squash": {
            "class": "float",
            "name": "squash",
            "value": 1.0
        },
        "squash_frequency": {
            "class": "int",
            "name": "squash_frequency",
            "value": 2
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 150.0
        }
    },
    "class": "ShaderNodeTexBrick",
    "inputs": {
        "Bias": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Bias",
            "name": "Bias",
            "value_type": "VALUE"
        },
        "Brick Width": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Brick Width",
            "name": "Brick Width",
            "value_type": "VALUE"
        },
        "Color1": {
            "class": "NodeSocketColor",
            "default_value": [
                0.800000011920929,
                0.800000011920929,
                0.800000011920929,
                1.0
            ],
            "identifier": "Color1",
            "name": "Color1",
            "value_type": "RGBA"
        },
        "Color2": {
            "class": "NodeSocketColor",
            "default_value": [
                0.20000000298023224,
                0.20000000298023224,
                0.20000000298023224,
                1.0
            ],
            "identifier": "Color2",
            "name": "Color2",
            "value_type": "RGBA"
        },
        "Mortar": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                1.0
            ],
            "identifier": "Mortar",
            "name": "Mortar",
            "value_type": "RGBA"
        },
        "Mortar Size": {
            "class": "NodeSocketFloat",
            "default_value": 0.019999999552965164,
            "identifier": "Mortar Size",
            "name": "Mortar Size",
            "value_type": "VALUE"
        },
        "Mortar Smooth": {
            "class": "NodeSocketFloat",
            "default_value": 0.10000000149011612,
            "identifier": "Mortar Smooth",
            "name": "Mortar Smooth",
            "value_type": "VALUE"
        },
        "Row Height": {
            "class": "NodeSocketFloat",
            "default_value": 0.25,
            "identifier": "Row Height",
            "name": "Row Height",
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

class _NodeWrapperShaderNodeTexBrick(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snTexBrick = _NodeWrapperShaderNodeTexBrick()
