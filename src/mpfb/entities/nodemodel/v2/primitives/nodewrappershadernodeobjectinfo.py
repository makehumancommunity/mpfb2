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
    "class": "ShaderNodeObjectInfo",
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
        "Location": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Location",
            "name": "Location",
            "value_type": "VECTOR"
        },
        "Material Index": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Material Index",
            "name": "Material Index",
            "value_type": "VALUE"
        },
        "Object Index": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Object Index",
            "name": "Object Index",
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

class _NodeWrapperShaderNodeObjectInfo(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snObjectInfo = _NodeWrapperShaderNodeObjectInfo()
