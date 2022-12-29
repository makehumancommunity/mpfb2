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
    "class": "ShaderNodeNormal",
    "inputs": {
        "Normal": {
            "class": "NodeSocketVectorDirection",
            "default_value": [
                0.0,
                0.0,
                1.0
            ],
            "identifier": "Normal",
            "name": "Normal",
            "value_type": "VECTOR"
        }
    },
    "outputs": {
        "Dot": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Dot",
            "name": "Dot",
            "value_type": "VALUE"
        },
        "Normal": {
            "class": "NodeSocketVectorDirection",
            "default_value": [
                0.0,
                0.0,
                1.0
            ],
            "identifier": "Normal",
            "name": "Normal",
            "value_type": "VECTOR"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeNormal(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snNormal = _NodeWrapperShaderNodeNormal()
