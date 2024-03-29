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
        "space": {
            "class": "enum",
            "name": "space",
            "value": "TANGENT"
        },
        "use_custom_color": {
            "class": "bool",
            "name": "use_custom_color",
            "value": false
        },
        "uv_map": {
            "class": "str",
            "name": "uv_map",
            "value": ""
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 150.0
        }
    },
    "class": "ShaderNodeNormalMap",
    "inputs": {
        "Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.5,
                0.5,
                1.0,
                1.0
            ],
            "identifier": "Color",
            "name": "Color",
            "value_type": "RGBA"
        },
        "Strength": {
            "class": "NodeSocketFloat",
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

class _NodeWrapperShaderNodeNormalMap(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snNormalMap = _NodeWrapperShaderNodeNormalMap()
