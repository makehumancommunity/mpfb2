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
        "inside": {
            "class": "bool",
            "name": "inside",
            "value": false
        },
        "location": {
            "class": "Vector",
            "name": "location",
            "value": [
                0.0,
                0.0
            ]
        },
        "only_local": {
            "class": "bool",
            "name": "only_local",
            "value": false
        },
        "samples": {
            "class": "int",
            "name": "samples",
            "value": 16
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeAmbientOcclusion",
    "inputs": {
        "Color": {
            "class": "NodeSocketColor",
            "default_value": [
                1.0,
                1.0,
                1.0,
                1.0
            ],
            "identifier": "Color",
            "name": "Color",
            "value_type": "RGBA"
        },
        "Distance": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Distance",
            "name": "Distance",
            "value_type": "VALUE"
        },
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
    },
    "outputs": {
        "AO": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "AO",
            "name": "AO",
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

class _NodeWrapperShaderNodeAmbientOcclusion(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snAmbientOcclusion = _NodeWrapperShaderNodeAmbientOcclusion()
