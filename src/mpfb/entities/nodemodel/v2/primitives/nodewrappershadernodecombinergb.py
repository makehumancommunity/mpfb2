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
    "class": "ShaderNodeCombineRGB",
    "inputs": {
        "B": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "B",
            "name": "B",
            "value_type": "VALUE"
        },
        "G": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "G",
            "name": "G",
            "value_type": "VALUE"
        },
        "R": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "R",
            "name": "R",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Image": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Image",
            "name": "Image",
            "value_type": "RGBA"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeCombineRGB(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snCombineRGB = _NodeWrapperShaderNodeCombineRGB()
