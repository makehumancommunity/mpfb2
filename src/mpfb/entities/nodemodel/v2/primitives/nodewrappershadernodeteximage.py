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
        "extension": {
            "class": "enum",
            "name": "extension",
            "value": "REPEAT"
        },
        "height": {
            "class": "float",
            "name": "height",
            "value": 100.0
        },
        "image": {
            "class": "NoneType",
            "name": "image",
            "value": null
        },
        "interpolation": {
            "class": "str",
            "name": "interpolation",
            "value": "Linear"
        },
        "location": {
            "class": "Vector",
            "name": "location",
            "value": [
                0.0,
                0.0
            ]
        },
        "projection": {
            "class": "enum",
            "name": "projection",
            "value": "FLAT"
        },
        "projection_blend": {
            "class": "float",
            "name": "projection_blend",
            "value": 0.0
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
    "class": "ShaderNodeTexImage",
    "inputs": {
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
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeTexImage(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snTexImage = _NodeWrapperShaderNodeTexImage()
