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
    "class": "ShaderNodePointInfo",
    "inputs": {},
    "outputs": {
        "Position": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Position",
            "name": "Position",
            "value_type": "VECTOR"
        },
        "Radius": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Radius",
            "name": "Radius",
            "value_type": "VALUE"
        },
        "Random": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Random",
            "name": "Random",
            "value_type": "VALUE"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodePointInfo(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snPointInfo = _NodeWrapperShaderNodePointInfo()
