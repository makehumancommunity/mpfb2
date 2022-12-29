import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "attributes": {
        "attribute_name": {
            "class": "str",
            "name": "attribute_name",
            "value": ""
        },
        "attribute_type": {
            "class": "enum",
            "name": "attribute_type",
            "value": "GEOMETRY"
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
    "class": "ShaderNodeAttribute",
    "inputs": {},
    "outputs": {
        "Alpha": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Alpha",
            "name": "Alpha",
            "value_type": "VALUE"
        },
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
        },
        "Fac": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Fac",
            "name": "Fac",
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
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeAttribute(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snAttribute = _NodeWrapperShaderNodeAttribute()
