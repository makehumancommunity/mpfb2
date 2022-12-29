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
            "value": 240.0
        }
    },
    "class": "ShaderNodeFloatCurve",
    "inputs": {
        "Factor": {
            "class": "NodeSocketFloatFactor",
            "default_value": 1.0,
            "identifier": "Factor",
            "name": "Factor",
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
        "Value": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Value",
            "name": "Value",
            "value_type": "VALUE"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeFloatCurve(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snFloatCurve = _NodeWrapperShaderNodeFloatCurve()
