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
        "mode": {
            "class": "enum",
            "name": "mode",
            "value": "RGB"
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeSeparateColor",
    "inputs": {
        "Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.800000011920929,
                0.800000011920929,
                0.800000011920929,
                1.0
            ],
            "identifier": "Color",
            "name": "Color",
            "value_type": "RGBA"
        }
    },
    "outputs": {
        "Blue": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Blue",
            "name": "Blue",
            "value_type": "VALUE"
        },
        "Green": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Green",
            "name": "Green",
            "value_type": "VALUE"
        },
        "Red": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Red",
            "name": "Red",
            "value_type": "VALUE"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeSeparateColor(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snSeparateColor = _NodeWrapperShaderNodeSeparateColor()
