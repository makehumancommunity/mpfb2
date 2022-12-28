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
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeLayerWeight",
    "inputs": {
        "Blend": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Blend",
            "name": "Blend",
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
        "Facing": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Facing",
            "name": "Facing",
            "value_type": "VALUE"
        },
        "Fresnel": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Fresnel",
            "name": "Fresnel",
            "value_type": "VALUE"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeLayerWeight(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snLayerWeight = _NodeWrapperShaderNodeLayerWeight()
