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
    "class": "ShaderNodeVolumeInfo",
    "inputs": {},
    "outputs": {
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
        "Density": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Density",
            "name": "Density",
            "value_type": "VALUE"
        },
        "Flame": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Flame",
            "name": "Flame",
            "value_type": "VALUE"
        },
        "Temperature": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Temperature",
            "name": "Temperature",
            "value_type": "VALUE"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeVolumeInfo(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snVolumeInfo = _NodeWrapperShaderNodeVolumeInfo()
