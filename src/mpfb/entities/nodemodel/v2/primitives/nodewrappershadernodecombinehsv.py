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
            "value": 140.0
        }
    },
    "class": "ShaderNodeCombineHSV",
    "inputs": {
        "H": {
            "class": "NodeSocketFloatUnsigned",
            "default_value": 0.0,
            "identifier": "H",
            "name": "H",
            "value_type": "VALUE"
        },
        "S": {
            "class": "NodeSocketFloatUnsigned",
            "default_value": 0.0,
            "identifier": "S",
            "name": "S",
            "value_type": "VALUE"
        },
        "V": {
            "class": "NodeSocketFloatUnsigned",
            "default_value": 0.0,
            "identifier": "V",
            "name": "V",
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

class _NodeWrapperShaderNodeCombineHSV(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snCombineHSV = _NodeWrapperShaderNodeCombineHSV()
