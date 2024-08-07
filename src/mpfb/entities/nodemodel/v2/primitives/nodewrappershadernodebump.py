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
        "invert": {
            "class": "bool",
            "name": "invert",
            "value": false
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
    "class": "ShaderNodeBump",
    "inputs": {
        "Distance": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Distance",
            "name": "Distance",
            "value_type": "VALUE"
        },
        "Height": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Height",
            "name": "Height",
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
        "Strength": {
            "class": "NodeSocketFloatFactor",
            "default_value": 1.0,
            "identifier": "Strength",
            "name": "Strength",
            "value_type": "VALUE"
        }
    },
    "outputs": {
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
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeBump(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snBump = _NodeWrapperShaderNodeBump()
