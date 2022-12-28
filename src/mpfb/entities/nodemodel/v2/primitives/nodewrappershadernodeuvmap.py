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
        "from_instancer": {
            "class": "bool",
            "name": "from_instancer",
            "value": false
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
        "uv_map": {
            "class": "str",
            "name": "uv_map",
            "value": ""
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 150.0
        }
    },
    "class": "ShaderNodeUVMap",
    "inputs": {},
    "outputs": {
        "UV": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "UV",
            "name": "UV",
            "value_type": "VECTOR"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeUVMap(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snUVMap = _NodeWrapperShaderNodeUVMap()
