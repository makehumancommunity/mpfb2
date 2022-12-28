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
    "class": "ShaderNodeCameraData",
    "inputs": {},
    "outputs": {
        "View Distance": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "View Distance",
            "name": "View Distance",
            "value_type": "VALUE"
        },
        "View Vector": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "View Vector",
            "name": "View Vector",
            "value_type": "VECTOR"
        },
        "View Z Depth": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "View Z Depth",
            "name": "View Z Depth",
            "value_type": "VALUE"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeCameraData(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snCameraData = _NodeWrapperShaderNodeCameraData()
