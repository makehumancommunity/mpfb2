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
    "class": "ShaderNodeHairInfo",
    "inputs": {},
    "outputs": {
        "Intercept": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Intercept",
            "name": "Intercept",
            "value_type": "VALUE"
        },
        "Is Strand": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Is Strand",
            "name": "Is Strand",
            "value_type": "VALUE"
        },
        "Length": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Length",
            "name": "Length",
            "value_type": "VALUE"
        },
        "Random": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Random",
            "name": "Random",
            "value_type": "VALUE"
        },
        "Tangent Normal": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Tangent Normal",
            "name": "Tangent Normal",
            "value_type": "VECTOR"
        },
        "Thickness": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Thickness",
            "name": "Thickness",
            "value_type": "VALUE"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeHairInfo(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snHairInfo = _NodeWrapperShaderNodeHairInfo()
