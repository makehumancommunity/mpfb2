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
        "filepath": {
            "class": "str",
            "name": "filepath",
            "value": ""
        },
        "height": {
            "class": "float",
            "name": "height",
            "value": 100.0
        },
        "ies": {
            "class": "NoneType",
            "name": "ies",
            "value": null
        },
        "location": {
            "class": "Vector",
            "name": "location",
            "value": [
                0.0,
                0.0
            ]
        },
        "mode": {
            "class": "enum",
            "name": "mode",
            "value": "INTERNAL"
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeTexIES",
    "inputs": {
        "Strength": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Strength",
            "name": "Strength",
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

class _NodeWrapperShaderNodeTexIES(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snTexIES = _NodeWrapperShaderNodeTexIES()
