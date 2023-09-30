import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "attributes": {
        "blend_type": {
            "class": "enum",
            "name": "blend_type",
            "value": "MIX"
        },
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
        "use_alpha": {
            "class": "bool",
            "name": "use_alpha",
            "value": false
        },
        "use_clamp": {
            "class": "bool",
            "name": "use_clamp",
            "value": false
        },
        "use_custom_color": {
            "class": "bool",
            "name": "use_custom_color",
            "value": false
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeMixRGB",
    "inputs": {
        "Color1": {
            "class": "NodeSocketColor",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ],
            "identifier": "Color1",
            "name": "Color1",
            "value_type": "RGBA"
        },
        "Color2": {
            "class": "NodeSocketColor",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ],
            "identifier": "Color2",
            "name": "Color2",
            "value_type": "RGBA"
        },
        "Fac": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.5,
            "identifier": "Fac",
            "name": "Fac",
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

class _NodeWrapperShaderNodeMixRGB(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snMixRGB = _NodeWrapperShaderNodeMixRGB()
