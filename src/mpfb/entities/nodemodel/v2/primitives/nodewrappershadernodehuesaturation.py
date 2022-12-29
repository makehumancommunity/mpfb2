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
        "use_custom_color": {
            "class": "bool",
            "name": "use_custom_color",
            "value": false
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 150.0
        }
    },
    "class": "ShaderNodeHueSaturation",
    "inputs": {
        "Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.8,
                0.8,
                0.8,
                1.0
            ],
            "identifier": "Color",
            "name": "Color",
            "value_type": "RGBA"
        },
        "Fac": {
            "class": "NodeSocketFloatFactor",
            "default_value": 1.0,
            "identifier": "Fac",
            "name": "Fac",
            "value_type": "VALUE"
        },
        "Hue": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Hue",
            "name": "Hue",
            "value_type": "VALUE"
        },
        "Saturation": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Saturation",
            "name": "Saturation",
            "value_type": "VALUE"
        },
        "Value": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Value",
            "name": "Value",
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
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeHueSaturation(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snHueSaturation = _NodeWrapperShaderNodeHueSaturation()
