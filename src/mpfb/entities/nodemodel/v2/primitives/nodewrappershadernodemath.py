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
        "operation": {
            "class": "enum",
            "name": "operation",
            "value": "ADD"
        },
        "use_clamp": {
            "class": "bool",
            "name": "use_clamp",
            "value": false
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeMath",
    "inputs": {
        "Value": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Value",
            "name": "Value",
            "value_type": "VALUE"
        },
        "Value_001": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Value_001",
            "name": "Value",
            "value_type": "VALUE"
        },
        "Value_002": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Value_002",
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

class _NodeWrapperShaderNodeMath(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snMath = _NodeWrapperShaderNodeMath()
