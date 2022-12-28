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
        "space": {
            "class": "enum",
            "name": "space",
            "value": "TANGENT"
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeVectorDisplacement",
    "inputs": {
        "Midlevel": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Midlevel",
            "name": "Midlevel",
            "value_type": "VALUE"
        },
        "Scale": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Scale",
            "name": "Scale",
            "value_type": "VALUE"
        },
        "Vector": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Vector",
            "name": "Vector",
            "value_type": "RGBA"
        }
    },
    "outputs": {
        "Displacement": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Displacement",
            "name": "Displacement",
            "value_type": "VECTOR"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeVectorDisplacement(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snVectorDisplacement = _NodeWrapperShaderNodeVectorDisplacement()
